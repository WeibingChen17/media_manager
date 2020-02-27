#!/usr/bin/python3 

import os
import sys
import time
import socket
import logging
from subprocess import call

import pymongo
from daemonize import Daemonize

from shared.constants import APP_NAME
from shared.constants import FORMAT
from shared.constants import LOCALHOST
from shared.constants import LOG_FILE
from shared.constants import MEDIA_MANAGER_PORT
from shared.constants import MONGO_PORT
from shared.constants import SUCCEED_CODE
from shared.jsonserver import JsonDataServer
from player.server import PlayerServer
from searcher.server import SearcherServer
from updater.server import UpdaterServer
from watcher.server import WatcherServer


class MediaManagerServer(JsonDataServer):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((LOCALHOST, MEDIA_MANAGER_PORT))
        self.host, self.port = self.socket.getsockname()
        self.log("Listening on {}:{}".format(self.host, self.port))
        self.client = pymongo.MongoClient(MONGO_PORT) 
        self.db = self.client["MediaManager"]
        self.col = self.db["RegisterApp"]
        self.log("Connecting to " + MONGO_PORT)
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

    def dispatch(self, msg):
        if msg["service"] == "GetServer":
            res = {"host" : "" , "port" : ""}
            server_name = msg["server_name"]
            if server_name in self.servers:
                server = self.servers[server_name]
                res = {"host" : server.get_host(), 
                        "port" : server.get_port(),
                        }
            return res
        elif msg["service"] == "GetDatabase":
            app_name = msg["app_name"]
            res = {"database" : "", "collection" : ""}
            entry = self.col.find_one({"app_name" : app_name})
            if entry == None:
                return res
            res["database"] = entry.get("database")
            res["collection"] = entry.get("collection")
            return res
        elif msg["service"] == "SetDatabase":
            app_name = msg["app_name"]
            self.col.update_one({"app_name" : app_name}, 
                    {"$set" : {"database" : msg["database"], "collection" : msg["collection"]}}, upsert=True)
            self.log("Update database of {}.".format(app_name))
            res = SUCCEED_CODE
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
        

if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    param = sys.argv[1]
    pidfile = "/tmp/%s-31425.pid" % APP_NAME

    if param == "start" and not os.path.exists(pidfile):
        daemon = Daemonize(app=APP_NAME, pid=pidfile, action=main)
        daemon.start()
    elif param == "stop" and os.path.exists(pidfile):
        with open(pidfile, "r") as f:
            pid = int(f.read())
            try:
                os.kill(pid, 15)
            except OSError:
                print("Could not stop server with Signal 15. Pid = ", pid)
                try:
                    os.kill(pid, 9)
                except OSError:
                    print("Could not stop server with Signal 9. Pid = ", pid)
                    print("Do it by yourself")
                else:
                    print("Server stopped. Pid = ", pid)
            else:
                print("Server stopped. Pid = ", pid)
    elif param == "status":
        print("running" if os.path.exists(pidfile) else "stop")
    elif param == "test":
        main()
    
