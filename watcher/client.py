#!/usr/bin/python3
import socket

from watcher.protocol import StringProtocol

class MediaWatcherClient:
    def __init__(self, mediaWatcherServer=None):
        if mediaWatcherServer:
            self.host = mediaWatcherServer.get_host()
            self.port = mediaWatcherServer.get_port()

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def __del__(self):
        self.socket.close()

    def watch(self, path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("MediaWatcherClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending ", path)
        self.socket.sendall(StringProtocol.encode(path.encode("utf8")))
        length, status = StringProtocol.decode(self.socket.recv(1024))
        assert(length == len(status))
        self.socket.close()
        return status.decode("utf8")

