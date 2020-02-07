import os
import time
import json
import socket
import threading
import hashlib

import pymongo
import filetype
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from shared.jsonserver import JsonDataServer
from shared.protocol import SUCCEED_CODE
from shared.protocol import FAIL_CODE

class Indexer:
    def __init__(self, collection):
        self.col = collection

    def index_file(self, file_path, reason, dest_path=""):
        path_query = {"path": file_path}
        if reason == "create":
            if self.col.count_documents(path_query) > 0:
                print("Ignore an existing file path")
                return "succeed"
            md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            md5_query =  {"md5": md5}
            doc = self.col.find(md5_query)
            if self.col.count_documents(md5_query) == 0:
                # unique new file: create a new doc
                entry = dict()
                entry["path"] = [file_path]
                entry["md5"] = hashlib.md5(open(file_path,'rb').read()).hexdigest()
                entry["release date"] = ""
                entry["actress"] = []
                entry["director"] = ""
                entry["maker"] = ""
                entry["disttributor"] = ""
                entry["rating"] = 0
                entry["tag"] = []
                entry["designation"] = ""
                # add size and duration
                entry["name"] = [os.path.basename(file_path)]
                entry["size"] = os.stat(file_path).st_size
                entry["type"] = filetype.guess(file_path)
                # todo: determine the best way of determinnig duration(ffprob)
                entry["duration"] = ""
                self.col.insert_one(entry)
            else:
                # the same file: append the path
                self.col.update(md5_query, {'$push': {"path" : file_path}})
            return "succeed"
        elif reason == "move":
            if self.col.count_documents(path_query) == 0:
                print("Ignore nonexisting file path")
                return "succeed"
            self.col.update(path_query, {
                '$push': {"path" : dest_path}, 
                '$push': {"name": os.path.basename(dest_path)}
                })
            self.col.update(path_query, {
                '$pull': {"path" : file_path},
                '$pull': {"name" : os.path.basename(file_path)}
                })
            return "succeed"
        elif reason == "delete":
            if self.col.count_documents(path_query) == 0:
                print("Ignore nonexisting file path")
                return "succeed"
            self.col.update(path_query, {'$pull': {"path" : file_path}})
            self.col.delete_many({"path" : []})
            return "succeed"
        else:
            return "fail"

    def index_folder(self, folder_path):
        for dirpath, _, names in os.walk(folder_path):
            for name in names:
                self.index_file(os.path.join(dirpath, name), "create")
        return "succeed"


class MediaFileEventHandler(RegexMatchingEventHandler):
    MEDIA_REGEX = [r".*\.mp4", r".*\.flv", r".*\.webm", r".*\.jpeg", r".*\.gif", r".*\.png", r".*\.jpg"]

    def __init__(self):
        super().__init__(self.MEDIA_REGEX)
        self.indexer = None

    def set_indexer(self, indexer):
        self.indexer = indexer

    def on_created(self, event):
        print("file {} is created".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "create")

    def on_moved(self, event):
        print("file {} is moved to {}".format(event.src_path, event.dest_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "move", event.dest_path)

    def on_deleted(self, event):
        print("file {} is deleted".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "delete")

    def on_modified(self, event):
        print("file {} is modified".format(event.src_path))


class MediaWatcherServer(JsonDataServer):
    def __init__(self):
        super().__init__()
        self.watchedFolder = []
        self.subthreads = []
        self.indexer = None
        self.mediaFileEventHandler = MediaFileEventHandler()
        self.log("Listening on {}:{}".format(self.host, self.port))

    def set_collection(self, collection):
        res = super().set_collection(collection)
        if res == SUCCEED_CODE:
            self.indexer = Indexer(self.col)
            self.mediaFileEventHandler.set_indexer(self.indexer)
        return res

    def get_watched_folder():
        return self.watchedFolder

    def dispatch(self, data):
        self.predispatch(data)
        if data["service"] == "watch":
            return self.watch(data["path"])
        else:
            return FAIL_CODE

    def watch(self, path):
        if os.path.exists(path):
            # (todo) avoid duplicate
            if path in self.watchedFolder:
                return SUCCEED_CODE
            self.watchedFolder.append(path)
            self.log("Indexing folder " +  path)
            self.indexer.index_folder(path)
            self.log("Watching folder " + path)
            thread = threading.Thread(target=self.monitor, args=(path,), name=path)
            self.subthreads.append(thread)
            thread.start()
            return SUCCEED_CODE
        else:
            self.log("Could not find path", path)
            return FAIL_CODE

    def monitor(self, path):
        observer = Observer()
        observer.schedule(self.mediaFileEventHandler, path, recursive=True)
        observer.start()
        t = threading.currentThread();
        while getattr(t, "do_run", True):
            time.sleep(1)
        observer.stop()
        observer.join()
        self.log("Stop watching " + path)

    def stop(self):
        for thread in self.subthreads:
            thread.do_run = False
            thread.join()
            self.log("Watching thread {} stops".format(thread.name))
        self.log("All watching threads stops")
        super().stop()

