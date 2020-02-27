import os
import time
import json
import socket
import threading
import logging 
from subprocess import  check_output, CalledProcessError, STDOUT 

import pymongo
import magic
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.constants import MediaEntry
from shared.constants import MEDIA_REGEX
from shared.constants import MEDIA_SUFFIX
from shared.jsonserver import JsonDataServer
from shared.constants import log_print

# copied from https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
def getDuration(filename):

    command = [
        'ffprobe', 
        '-v', 
        'error', 
        '-show_entries', 
        'format=duration', 
        '-of', 
        'default=noprint_wrappers=1:nokey=1', 
        filename
      ]

    try:
        output = check_output( command, stderr=STDOUT ).decode()
    except CalledProcessError as e:
        output = e.output.decode()

    return output.strip("\n")


class Indexer:
    def __init__(self, collection):
        self.col = collection

    def log(self, msg):
        log_print("Indexer", msg)

    def index_file(self, file_path, reason, dest_path=""):
        path_query = {"path" : file_path}
        if reason == "create":
            if self.col.count_documents(path_query) > 0:
                self.log("Ignore an existing file path")
                return SUCCEED_CODE
            entry = MediaEntry()
            entry.path = file_path
            entry.name = os.path.basename(file_path)
            entry.size = os.stat(file_path).st_size
            guesstype = magic.from_file(file_path, mime=True)
            entry.type = guesstype if guesstype else "unknown"
            if entry.type.startswith("video"):
                entry.duration = getDuration(file_path)
            self.col.insert_one(entry.asdict())
            return SUCCEED_CODE
        elif reason == "move":
            if self.col.count_documents(path_query) == 0:
                self.log("Ignore nonexisting file path")
                return "succeed"
            res = self.col.update(path_query, {
                '$set': {"path" : dest_path, "name" : os.path.basename(dest_path)},
                })
            return SUCCEED_CODE
        elif reason == "delete":
            if self.col.count_documents(path_query) == 0:
                self.log("Ignore nonexisting file path")
                return SUCCEED_CODE
            res = self.col.delete_one({"path" : file_path})
            return SUCCEED_CODE
        else:
            return FAIL_CODE


class MediaFileEventHandler(RegexMatchingEventHandler):

    def __init__(self, indexer):
        super().__init__(MEDIA_REGEX)
        self.indexer = indexer
        
    def log(self, msg):
        log_print("MediaFileEventHandler", msg)

    def on_created(self, event):
        self.log("File {} is created".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "create")

    def on_moved(self, event):
        self.log("File {} is moved to {}".format(event.src_path, event.dest_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "move", event.dest_path)

    def on_deleted(self, event):
        self.log("File {} is deleted".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "delete")


class WatcherServer(JsonDataServer):
    def __init__(self):
        super().__init__()
        self.watchedFolder = []
        self.subthreads = {}

    def get_watched_folder():
        return self.watchedFolder

    def dispatch(self, msg):
        if msg["service"] == "watch":
            return self.watch(self.getCollection(msg), msg["path"], msg["force_scan"])
        elif msg["service"] == "unwatch":
            return self.unwatch(self.getCollection(msg), msg["path"])
        else:
            return FAIL_CODE

    def watch(self, col, path, force_scan=False):
        self.log(path)
        if os.path.exists(path):
            if force_scan == False and (col, path) in self.watchedFolder:
                    self.log("{} is already watched in {}".format(path, col))
                    return SUCCEED_CODE
            if (col, path) not in self.watchedFolder:
                self.watchedFolder.append((str(col), path))

            self.log("Watching folder {} for {}".format(path, col))
            thread = threading.Thread(target=self.monitor, args=(col, path,), name=path)
            self.subthreads.update({(str(col), path) : thread})
            thread.start()
            return SUCCEED_CODE
        else:
            self.log("Could not find path", path)
            return FAIL_CODE

    def unwatch(self, col, path):
        if (col, path) not in self.subthreads:
            return SUCCEED_CODE
        try:
            self.watchedFolder.remove((col, path))
            thread = self.subthreads[(col, path)]
            thread.do_run = False
            observer.join()
            self.log("Stop watching " + path)
            return SUCCEED_CODE
        except:
            return FAIL_CODE

    def monitor(self, col, path):
        observer = Observer()
        indexer = Indexer(col)
        observer.schedule(MediaFileEventHandler(indexer), path, recursive=True)
        observer.start()
        self.log("Indexing folder " +  path)
        for dirpath, _, names in os.walk(path):
            for name in names:
                if any([name.endswith(suf) for suf in MEDIA_SUFFIX]):
                    # (todo) deal with failure
                    self.log("Indexing " + name)
                    indexer.index_file(os.path.join(dirpath, name), "create")
        t = threading.currentThread();
        while getattr(t, "do_run", True):
            time.sleep(1)
        observer.stop()
        observer.join()
        self.log("Stop watching " + path)

    def stop(self):
        for thread in self.subthreads.values():
            thread.do_run = False
            thread.join()
            self.log("Watching thread {} stops".format(thread.name))
        self.log("All watching threads stops")
        super().stop()

