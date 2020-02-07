import uuid

from daemonize import Daemonize

from player.server import PlayerServer
from updater.server import UpdaterServer
from searcher.server import SearcherServer
from watcher.server import WatcherServer

class MediaManagerServer(JsonServer):
    HOST = "127.0.0.1"
    PORT = 31425

    def __init__(self):
        super().__init__()
        self.servers = {
                "watcher" : WatcherServer(), 
                "player" : PlayerServer(),
                "searcher" : PlayerServer(), 
                "updater" : UpdaterServer(),
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
    with MediaManagerServer() as mediaManagerServer:
        while true:
            pass

if __name__ == '__main__':
        myname = "media_manager"
        pidfile='/tmp/%s-%s' % (myname, uuid.uuid1())
        daemon = Daemonize(app=myname,pid=pidfile, action=main)
        daemon.start()
