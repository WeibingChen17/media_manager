import json
import socket

from shared.protocol import StringProtocol

class MediaWatcherClient:
    def __init__(self, mediaWatcherServer=None):
        self.host = None
        self.port = None
        if mediaWatcherServer:
            self.host = mediaWatcherServer.get_host()
            self.port = mediaWatcherServer.get_port()

    def __repr__(self):
        return "MediaWatcherClient [host : {}, port : {}]".format(self.host, self.port)

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def watch(self, path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("MediaWatcherClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending", path)
        data = {"reason" : "watch", "path": path}
        self.socket.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, status = StringProtocol.decode(self.socket.recv(1024))
        assert(length == len(status))
        self.socket.close()
        return status.decode("utf8")

    def set_indexer(self, indexerClient):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print("MediaWatcherClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending indexer", indexerClient)
        data = {"reason" : "indexer", "host": indexerClient.get_host(), "port": indexerClient.get_port()}
        s.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, status = StringProtocol.decode(s.recv(1024))
        assert(length == len(status))
        s.close()
        return status.decode("utf8")

