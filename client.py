import sys

from shared.jsonclient import JsonClient
from shared.constants import LOCALHOST
from shared.constants import MEDIA_MANAGER_PORT
from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.constants import APP_NAME_EXISTED
from shared.constants import APP_NAME_NONEXISTED
from player.client import PlayerClient
from watcher.client import WatcherClient
from updater.client import UpdaterClient
from searcher.client import SearcherClient
from cmdclient import CmdClient

class MediaManagerClient(JsonClient):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.set_host = LOCALHOST
        self.set_port(MEDIA_MANAGER_PORT)
        self.watch_folders = []
        self.database = ""
        self.collection = ""
        self.cmdClient = None
        self.clients = {
            "Player" : PlayerClient(),
            "Watcher" : WatcherClient(),
            "Updater" : UpdaterClient(),
            "Searcher" : SearcherClient()
            }

    def set_name(self, name):
        self.name = name
        res = self._send({"service" : "GetDatabase", "app_name" : self.name})
        database = res["database"]
        collection = res["collection"]
        if database != "" and collection != "":
            self.database = database
            self.collection = collection
            return APP_NAME_EXISTED
        else:
            return APP_NAME_NONEXISTED

    def set_database(self, database, collection):
        self.database = database
        self.collection = collection
        return self._send({"service" : "SetDatabase", "app_name" : self.name, 
            "database" : self.database, "collection" : self.collection})

    def add_watch_folder(self, watch_folder, force_scan=False):
        self.watch_folders.append((watch_folder, force_scan))

    def _scan_watch_folder(self):
        if not self.watcher or not self.watch_folders:
            return
        for path, force_scan in self.watch_folders:
            print("Watching {}".format(path))
            self.watcher.watch(path, force_scan)

    def _query(self, server_name):
        # exception handling
        try:
            return self._send({"service" : "GetServer", "server_name" : server_name})
        except Exception as e:
            print("Server may not be running. Try ./server.py start " )
            sys.exit(1)

    def _get_all_clients(self):
        for name, client in self.clients.items():
            res = self._query(name)
            client.set_host(res["host"])
            client.set_port(res["port"])

        if not self.database or not self.collection:
            raise Exception("Need to set up databse and collection before run")

        for name, client in self.clients.items():
            if hasattr(client, "set_database"):
                client.set_database(self.database, self.collection)


    def run(self):
        self._get_all_clients()
        self.player = self.clients["Player"]
        self.watcher = self.clients["Watcher"]
        self.updater = self.clients["Updater"]
        self.searcher = self.clients["Searcher"]

        self._scan_watch_folder()

        self.cmdClient = CmdClient(self.name, self.searcher, self.player, self.updater)

        try:
            self.cmdClient.cmdloop()
        except KeyboardInterrupt:
            pass

