import os
import time
import json
import socket
import threading
import hashlib
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
        self.log = logging.info

    def set_log(self, log):
        self.log = log

    def index_file(self, file_path, reason, dest_path=""):
        path_query = {"path" : file_path}
        if reason == "create":
            if self.col.count_documents(path_query) > 0:
                self.log("Ignore an existing file path")
                return SUCCEED_CODE
            md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            md5_query =  {"md5": md5}
            if self.col.count_documents(md5_query) == 0:
                # unique new file: create a new doc
                entry = MediaEntry()
                entry.path = [file_path]
                entry.md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()
                # add size and duration
                entry.name = [os.path.basename(file_path)]
                entry.size = os.stat(file_path).st_size
                guesstype = magic.from_file(file_path, mime=True)
                entry.type = guesstype if guesstype else "unknown"
                if entry.type.startswith("video"):
                    entry.duration = getDuration(file_path)
                self.col.insert_one(entry.asdict())
            else:
                # the same file: append the path
                self.col.update(md5_query, {'$push': {"path" : file_path}})
            return SUCCEED_CODE
        elif reason == "move":
            if self.col.count_documents(path_query) == 0:
                self.log("Ignore nonexisting file path")
                return "succeed"
            self.col.update(path_query, {
                '$push': {"path" : dest_path}, 
                '$push': {"name": os.path.basename(dest_path)}
                })
            self.col.update(path_query, {
                '$pull': {"path" : file_path},
                '$pull': {"name" : os.path.basename(file_path)}
                })
            return SUCCEED_CODE
        elif reason == "delete":
            if self.col.count_documents(path_query) == 0:
                self.log("Ignore nonexisting file path")
                return SUCCEED_CODE
            self.col.update(path_query, {'$pull': {"path" : file_path}})
            self.col.delete_many({"path" : []})
            return SUCCEED_CODE
        elif reason == "modified":
            # todo
            pass
        else:
            return FAIL_CODE


class MediaFileEventHandler(RegexMatchingEventHandler):

    def __init__(self):
        super().__init__(MEDIA_REGEX)
        self.indexer = None
        self.log = logging.info

    def set_log(self, log):
        self.log = log

    def set_indexer(self, indexer):
        self.indexer = indexer

    def on_created(self, event):
        self.log("file {} is created".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "create")

    def on_moved(self, event):
        self.log("file {} is moved to {}".format(event.src_path, event.dest_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "move", event.dest_path)

    def on_deleted(self, event):
        self.log("file {} is deleted".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "delete")

    def on_modified(self, event):
        self.log("file {} is modified".format(event.src_path))
        if self.indexer:
            self.indexer.index_file(event.src_path, "modified")


class WatcherServer(JsonDataServer):
    def __init__(self):
        super().__init__()
        self.watchedFolder = []
        self.subthreads = []
        self.indexer = None
        self.mediaFileEventHandler = MediaFileEventHandler()

    def set_collection(self, collection):
        res = super().set_collection(collection)
        if res == SUCCEED_CODE:
            self.indexer = Indexer(self.col)
            self.indexer.set_log(self.log)
            self.mediaFileEventHandler.set_indexer(self.indexer)
            self.mediaFileEventHandler.set_log(self.log)
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
            if path in self.watchedFolder:
                self.log("{} is already watched".format(path))
                return SUCCEED_CODE
            self.watchedFolder.append(path)

            self.log("Watching folder " + path)
            thread = threading.Thread(target=self.monitor, args=(path,), name=path)
            self.subthreads.append(thread)
            thread.start()
            return SUCCEED_CODE
        else:
            self.log("Could not find path", path)
            return FAIL_CODE

    def index_media_folder(self, folder_path):
        self.log("Indexing folder " +  folder_path)
        for dirpath, _, names in os.walk(folder_path):
            for name in names:
                if any([name.endswith(suf) for suf in MEDIA_SUFFIX]):
                    # (todo) deal with failure
                    self.log("Indexing " + name)
                    self.indexer.index_file(os.path.join(dirpath, name), "create")
        # assuem happy
        return SUCCEED_CODE

    def monitor(self, path):
        observer = Observer()
        observer.schedule(self.mediaFileEventHandler, path, recursive=True)
        observer.start()
        self.index_media_folder(path)
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

