#!/usr/bin/python3
import socket
from shared.protocol import StringProtocol

class PlayerClient:
    def __init__(self, playerServer):
        self.host = playerServer.get_host()
        self.port = playerServer.get_port()

    def __repr__(self):
        return "PlayerClient [host : {}, port : {}]".format(self.host, self.port)

    def play(self, path):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print("PlayerClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending ", path)
        s.sendall(StringProtocol.encode(path.encode("utf8")))
        length, status = StringProtocol.decode(s.recv(1024))
        assert(length == len(status))
        s.close()
        return status.decode("utf8")

