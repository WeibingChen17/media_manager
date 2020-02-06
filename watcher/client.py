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

    def set_database(self, database):
        return self._send({"reason" : "set_database", "database" : database})

    def set_collection(self, collection):
        return self._send({"reason" : "set_collection", "collection" : collection})

    def watch(self, path):
        data = {"reason" : "watch", "path": path}
        return self._send(data)

    def _send(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print("MediaWatcherClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending", data)
        s.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, status = StringProtocol.decode(s.recv(1024))
        assert(length == len(status))
        s.close()
        return status.decode("utf8")

