#!/usr/bin/python3
import socket
from .protocol import StringProtocol

class PlayerClient:
    def __init__(self, playerServer):
        self.host = playerServer.get_host()
        self.port = playerServer.get_port()

    def __del__(self):
        self.socket.close()

    def play(self, path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("PlayerClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending ", path)
        self.socket.sendall(StringProtocol.encode(path.encode("utf8")))
        length, status = StringProtocol.decode(self.socket.recv(1024))
        assert(length == len(status))
        self.socket.close()
        return status.decode("utf8")

