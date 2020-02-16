#!/usr/bin/python3 

import os
import sys
import time
import socket
from subprocess import call

from daemonize import Daemonize

from shared.jsonserver import JsonServer
from shared.protocol import LOCALHOST
from shared.protocol import MEDIA_MANAGER_PORT
from player.server import PlayerServer
from updater.server import UpdaterServer
from searcher.server import SearcherServer
from watcher.server import WatcherServer

app_name = "media_manager"
log_file = "/var/log/media_manager/log"

class MediaManagerServer(JsonServer):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((LOCALHOST, MEDIA_MANAGER_PORT))
        self.host, self.port = self.socket.getsockname()
        self.log("Listening on {}:{}".format(self.host, self.port))
        self.servers = {
                "Watcher" : WatcherServer(), 
                "Player" : PlayerServer(),
                "Searcher" : SearcherServer(), 
                "Updater" : UpdaterServer(),
                }

    def start(self):
        for _, server in self.servers.items():
            server.start()
        super().start()
    
    def stop(self):
        for _, server in self.servers.items():
            server.stop()
        super().stop()

    def dispatch(self, data):
        res = {"host" : "" , "port" : ""}
        if data["service"] == "GetServer":
            server_name = data["server_name"]
            if server_name in self.servers:
                server = self.servers[server_name]
                res = {"host" : server.get_host(), 
                        "port" : server.get_port(),
                        }
        return res

def main():
    saved_stdout = sys.stdout
    try:
        with open(log_file, 'a+') as log, MediaManagerServer() as mediaManagerServer:
            sys.stdout = log
            while True:
                # Sleep the main thread to reduce cpu usage
                time.sleep(1000)
                log.flush()
    except KeyboardInterrupt:
        pass
    except OSError:
        print("Port is used. Manybe a media manager is already running.")
    finally:
        sys.stdout = saved_stdout
        mediaManagerServer.stop()
        

if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    param = sys.argv[1]
    pidfile = "/tmp/%s-31425.pid" % app_name

    if param == "start" and not os.path.exists(pidfile):
        daemon = Daemonize(app=app_name, pid=pidfile, action=main)
        daemon.start()
    elif param == "stop" and os.path.exists(pidfile):
        with open(pidfile, "r") as f:
            status = call(["kill", f.read()])
            print(status)
    elif param == "status":
        print("running" if os.path.exists(pidfile) else "stop")
    elif param == "test":
        main()
    
