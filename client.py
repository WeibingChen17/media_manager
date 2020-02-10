import sys

from shared.jsonclient import JsonClient
from shared.protocol import LOCALHOST
from shared.protocol import MEDIA_MANAGER_PORT
from player.client import PlayerClient
from watcher.client import WatcherClient
from updater.client import UpdaterClient
from searcher.client import SearcherClient

SEARCH_PROMPT = "Search : " 
PLAY_PROMPT = "PLAY : "
EDIT_PROMPT = "Edit : "

class MediaManagerClient(JsonClient):
    def __init__(self):
        super().__init__()
        self.set_host = LOCALHOST
        self.set_port(MEDIA_MANAGER_PORT)
        self.watch_folders = []
        self.database = ""
        self.collection = ""
        self.clients = {
            "Player" : PlayerClient(),
            "Watcher" : WatcherClient(),
            "Updater" : UpdaterClient(),
            "Searcher" : SearcherClient()
            }

    def set_database(self, database):
        self.database = database

    def set_collection(self, collection):
        self.collection = collection

    def set_watch_folders(self, watch_folders):
        assert(isinstance(watch_folders, list))
        self.watch_folders = watch_folders[:]

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
            raise Exception("Need to set up databse and collection before tun")

        for name, client in self.clients.items():
            if hasattr(client, "set_database"):
                client.set_database(self.database)
            if hasattr(client, "set_collection"):
                client.set_collection(self.collection)


    def run(self):
        self._get_all_clients()
        self.player = self.clients["Player"]
        self.watcher = self.clients["Watcher"]
        self.updater = self.clients["Updater"]
        self.searcher = self.clients["Searcher"]

        for path in self.watch_folders:
            self.watcher.watch(path)

        query = input(SEARCH_PROMPT)
        while query:
            res = self.searcher.search(query)
            self.show_search_result(res)
            if res:
                self.play(res)
            query = input(SEARCH_PROMPT)

    def show_search_result(self, res):
        for ind, entry in enumerate(res):
            print(" {index} {name} ".format(index=ind, name=entry.name))


    def play(self, res):
            play_id = input(PLAY_PROMPT)
            while play_id:
                if play_id == "show":
                    self.show_search_result(res)
                elif play_id != "edit":
                    self.player.play(res[int(play_id)].path[0])
                else:
                    self.edit(res)
                play_id = input(PLAY_PROMPT)

    def edit(self, res):
            edit_id = input(EDIT_PROMPT)
            while edit_id:
                mediaEntry = res[int(edit_id)]
                print("The entry to edit:\n" + str(mediaEntry))
                entry_id = mediaEntry._id
                command = input("enter command :")
                while command:
                    if command == "delete":
                        self.updater.delete(entry_id)
                        print("entry {} is deleted".format(entry_id))
                    elif command == "show":
                        mediaEntry = self.searcher.search_by_id(entry_id)[0]
                        print("Update entry to edit:\n" + str(mediaEntry))
                    else:
                        op, field, values = command.split()
                        for value in values.split(","):
                            query = {op : {field : value}}
                            self.updater.update(entry_id, query)
                    command = input("enter command :")
                edit_id = input(EDIT_PROMPT)


