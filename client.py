import sys

from shared.jsonclient import JsonClient
from shared.constants import LOCALHOST
from shared.constants import MEDIA_MANAGER_PORT
from player.client import PlayerClient
from watcher.client import WatcherClient
from updater.client import UpdaterClient
from searcher.client import SearcherClient

SEARCH_PROMPT = "SEARCH : " 
PLAY_PROMPT = "PLAY : "
EDIT_PROMPT = "EDIT : "

def _checkIndexRange(ind, lst):
    try:
        ind = int(ind)
    except ValueError as e:
        print("Index must be integer")
        return None
    if ind < 0 or ind > len(lst):
        print("Index is out of range")
        return None
    return ind

class MediaManagerClient(JsonClient):
    def __init__(self):
        super().__init__()
        self.name = ""
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

    def set_name(self, name):
        self.name = name

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
            try:
                query = eval("{" + query + "}")
            except:
                pass
            res = self.searcher.search(query)
            self.show_search_result(res)
            if res:
                self.play(res)
            query = input(SEARCH_PROMPT)

    def show_search_result(self, res, extra=None):
        if extra == "sort size":
            filter_res = sorted(res, key=lambda entry:entry.size, reverse=True)
        elif extra == "sort name":
            filter_res = sorted(res, key=lambda entry:entry.name)
        elif extra == "only video":
            filter_res = [entry for entry in res if entry.type and entry.type.startswith("video")]
        else:
            filter_res = res
        for ind, entry in enumerate(filter_res):
            print("{index:<5} {size:<10} {name} ".format(index=ind, name=str(entry.name), size=entry.size))

    def play(self, res):
            play_id = input(PLAY_PROMPT)
            while play_id:
                play_id = play_id.strip()
                if play_id == "show":
                    self.show_search_result(res)
                elif play_id in ["sort name", "sort size", "only video"]:
                    self.show_search_result(res, play_id)
                elif play_id == "edit":
                    self.edit(res)
                else:
                    ind = _checkIndexRange(play_id, res)
                    if ind:
                        self.player.play(res[ind].path[0])
                play_id = input(PLAY_PROMPT)

    def edit(self, res):
            edit_id = input(EDIT_PROMPT)
            while edit_id:
                if edit_id == "show":
                    self.show_search_result(res) 
                    edit_id = input(EDIT_PROMPT)
                    continue
                ind = _checkIndexRange(edit_id, res)
                if ind == None:
                    edit_id = input(EDIT_PROMPT)
                    continue
                mediaEntry = res[ind]
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
                        op, field, *values = command.split()
                        if hasattr(mediaEntry, field):
                            if (op == "add" or op == "remove") and not isinstance(mediaEntry.__dict__[field], list):
                                print("Operation is not supported in this field. Use `change` instead")
                            elif field in ["name", "size", "type", "duration"]:
                                print("Immutable Field: {}".format(field))
                            else:
                                queryList = []
                                for value in " ".join(values).split(","):
                                    queryList.append({op : {field : value.strip('"')}})
                                self.updater.update_all(entry_id, queryList)
                        else:
                            print("No such field in MediaEntry")
                    command = input("enter command :")
                edit_id = input(EDIT_PROMPT)


