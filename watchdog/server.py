import os
import time
import socket
import threading
from watchdog.observers import Observer
from media_file_event_handler import MediaFileEventHandler
from protocol import StringProtocol

HOST = "127.0.0.1"

def monitor(path):
    observer = Observer()
    observer.schedule(MediaFileEventHandler(), path, recursive=True)
    observer.start()
    t = threading.currentThread();
    while getattr(t, "do_run", True):
        time.sleep(1)
    observer.stop()
    observer.join()
    print("Stop watching ", path)

class MediaWatcherServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.watchedFolder = []
        self.subthreads = []
        print("MediaWatcher is listening on {}:{}".format(self.host, self.port))

    def __del__(self):
        self.socket.close()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_watched_folder():
        return self.watchedFolder

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
                status = self.watch(received_data)
                conn.send(StringProtocol.encode(status))

    def watch(self, byte):
        path = byte.decode("utf8")
        if os.path.exists(path):
            # (todo) avoid duplicate
            self.watchedFolder.append(path)
            print("Watching folder ", path)
            thread = threading.Thread(target=monitor, args=(path,), name=path)
            self.subthreads.append(thread)
            thread.start()
            return b"succeed"
        else:
            print("Could not find path", path)
            return b"fail"

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

def main():
    try:
        mediaWatcherServer = MediaWatcherServer()
        mediaWatcherServer.start()
    finally:
        mediaWatcherServer.stop()

if __name__ == "__main__":
    main()
