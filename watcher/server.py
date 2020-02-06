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

from shared.protocol import StringProtocol

HOST = "127.0.0.1"

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


class MediaWatcherServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.watchedFolder = []
        self.subthreads = []
        self.client = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.indexer = None
        self.db = None
        self.col = None
        self.mediaFileEventHandler = MediaFileEventHandler()
        print("MediaWatcher is listening on {}:{}".format(self.host, self.port))

    def __del__(self):
        self.socket.close()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def set_database(self, database):
        self.db = self.client[database]
        print("Use Database {}".format(database))
        return "succeed"

    def set_collection(self, collection):
        if not self.db:
            raise Exception("No database is selected yet")
        self.col = self.db[collection]
        print("Use Collection {}".format(collection))
        self.indexer = Indexer(self.col)
        self.mediaFileEventHandler.set_indexer(self.indexer)
        return "succeed"

    def get_watched_folder():
        return self.watchedFolder

    def set_indexer(self, host, port):
        self.indexer.set_host(host)
        self.indexer.set_port(port)
        self.mediaFileEventHandler.set_indexer(self.indexer)
        print("Use indexer", self.indexer)
        return "succeed"

    def start(self):
        self.thread = threading.Thread(target=self.__run, args=())
        self.thread.start()
        print("MediaWatcherServer starts")

    def __run(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.socket.listen()
            conn, addr = self.socket.accept()
            received_data = []
            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                if not data:
                    break
                length, data = StringProtocol.decode(data)
                totalLength = length
                received_data.append(data)
                print("Receive {} bytes".format(len(data)))
                while length - len(data) > 0:
                    length -= len(data)
                    data = conn.recv(1024)
                    print("Receive {} bytes".format(len(data)))
                    received_data.append(data)
                received_data = b''.join(received_data)
                print("Receive {} bytes in total".format(len(received_data)))
                assert(len(received_data) == totalLength)
                status = self.dispatch(received_data)
                conn.send(StringProtocol.encode(status.encode("utf8")))

    def dispatch(self, byte):
        data = json.loads(byte.decode("utf8"))
        if data["reason"] == "set_database":
            return self.set_database(data["database"])
        elif data["reason"] == "set_collection":
            return self.set_collection(data["collection"])
        elif data["reason"] == "indexer":
            return self.set_indexer(data["host"], data["port"])
        elif data["reason"] == "watch":
            return self.watch(data["path"])
        else:
            return "fail"

    def watch(self, path):
        if os.path.exists(path):
            # (todo) avoid duplicate
            self.watchedFolder.append(path)
            print("Indexing folder ", path)
            self.indexer.index_folder(path)
            print("Watching folder ", path)
            thread = threading.Thread(target=self.monitor, args=(path,), name=path)
            self.subthreads.append(thread)
            thread.start()
            return "succeed"
        else:
            print("Could not find path", path)
            return "fail"

    def monitor(self, path):
        observer = Observer()
        observer.schedule(self.mediaFileEventHandler, path, recursive=True)
        observer.start()
        t = threading.currentThread();
        while getattr(t, "do_run", True):
            time.sleep(1)
        observer.stop()
        observer.join()
        print("Stop watching ", path)

    def stop(self):
        for thread in self.subthreads:
            thread.do_run = False
            thread.join()
            print("Watching thread {} stops".format(thread.name))
        print("All watching threads stops")
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()
        print("Main thread stops")
        print("MediaWatcherServer stops")

