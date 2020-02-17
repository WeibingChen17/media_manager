#!/usr/bin/python3 

import os
import logging
import time
import socket
import sys
from subprocess import call

from daemonize import Daemonize

from shared.constants import LOCALHOST
from shared.constants import MEDIA_MANAGER_PORT
from shared.constants import APP_NAME
from shared.constants import FORMAT
from shared.constants import LOG_FILE
from shared.jsonserver import JsonServer
from player.server import PlayerServer
from updater.server import UpdaterServer
from searcher.server import SearcherServer
from watcher.server import WatcherServer


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
    try:
        logging.basicConfig(format=FORMAT, filename=LOG_FILE, filemode='a+', level=logging.DEBUG)
        with MediaManagerServer() as mediaManagerServer:
            while True:
                # Sleep the main thread to reduce cpu usage
                time.sleep(1000)
    except KeyboardInterrupt:
        pass
    except OSError:
        print("Port is used. Manybe a media manager is already running.")
    finally:
        mediaManagerServer.stop()
        

if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    param = sys.argv[1]
    pidfile = "/tmp/%s-31425.pid" % APP_NAME

    if param == "start" and not os.path.exists(pidfile):
        daemon = Daemonize(app=APP_NAME, pid=pidfile, action=main)
        daemon.start()
    elif param == "stop" and os.path.exists(pidfile):
        with open(pidfile, "r") as f:
            status = call(["kill", f.read()])
            print(status)
    elif param == "status":
        print("running" if os.path.exists(pidfile) else "stop")
    elif param == "test":
        main()
    
