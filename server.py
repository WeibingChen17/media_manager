#!/usr/bin/python3 

import os
import sys
import socket
from subprocess import call

from daemonize import Daemonize

from shared.jsonserver import JsonServer
from shared.protocol import LOCALHOST
from player.server import PlayerServer
from updater.server import UpdaterServer
from searcher.server import SearcherServer
from watcher.server import WatcherServer

PORT = 31425

class MediaManagerServer(JsonServer):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((LOCALHOST, PORT))
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
        with MediaManagerServer() as mediaManagerServer:
            while True:
                pass
    except KeyboardInterrupt:
        pass
    except OSError:
        print("Port is used. Manybe a media manager is already running.")
        

if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    app_name = "media_manager"
    pidfile = '/tmp/%s-31425.pid' % app_name
    if sys.argv[1] == "start" and not os.path.exists(pidfile):
        daemon = Daemonize(app=app_name, pid=pidfile, action=main)
        daemon.start()
    elif sys.argv[1] == "stop" and os.path.exists(pidfile):
        with open(pidfile, "r") as f:
            status = call(["kill", f.read()])
            print(status)
    
