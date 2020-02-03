import os
import time
import json
import socket
import threading

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from indexer.client import IndexerClient
from shared.protocol import StringProtocol

HOST = "127.0.0.1"

class MediaFileEventHandler(RegexMatchingEventHandler):
    MEDIA_REGEX = [r".*\.mp4", r".*\.flv", r".*\.webm", r".*\.jpeg", r".*\.gif", r".*\.png", r".*\.jpg"]

    def __init__(self):
        super().__init__(self.MEDIA_REGEX)
        self.indexerClient = None

    def set_indexer(self, indexer):
        self.indexerClient = indexer

    def on_created(self, event):
        print("file {} is created".format(event.src_path))
        if self.indexerClient:
            self.indexerClient.index_file(event.src_path, "create")

    def on_moved(self, event):
        print("file {} is moved to {}".format(event.src_path, event.dest_path))
        if self.indexerClient:
            self.indexerClient.index_file(event.src_path, "move", event.dest_path)

    def on_deleted(self, event):
        print("file {} is deleted".format(event.src_path))
        if self.indexerClient:
            self.indexerClient.index_file(event.src_path, "delete")

    def on_modified(self, event):
        print("file {} is modified".format(event.src_path))


class MediaWatcherServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.watchedFolder = []
        self.subthreads = []
        self.indexer = IndexerClient()
        self.mediaFileEventHandler = MediaFileEventHandler()
        print("MediaWatcher is listening on {}:{}".format(self.host, self.port))

    def __del__(self):
        self.socket.close()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

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
        if data["reason"] == "indexer":
            return self.set_indexer(data["host"], data["port"])
        elif data["reason"] == "watch":
            return self.watch(data["path"])

    def watch(self, path):
        if os.path.exists(path):
            # (todo) avoid duplicate
            self.watchedFolder.append(path)
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

