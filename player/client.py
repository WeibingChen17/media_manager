#!/usr/bin/python3
import socket
from protocol import PlayerProtocol

class PlayerClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __del__(self):
        self.socket.close()

    def play(self, path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("PlayerClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending ", path)
        self.socket.send(PlayerProtocol.encode(path.encode("utf8")))
        length, status = PlayerProtocol.decode(self.socket.recv(1024))
        assert(length == len(status))
        self.socket.close()
        return status.decode("utf8")

