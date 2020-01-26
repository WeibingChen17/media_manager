import socket
import threading
import os
from subprocess import call

from protocol import PlayerProtocol

HOST = "127.0.0.1"
PORT = 65000

def dispatch(path_string):
    target = path_string
    if target.endswith("pdf"):
        call(["evince", target])
    elif target.endswith("jpg") or target.endswith("jpeg") or target.endswith("png") or target.endswith("gif"):
        call(["feh", target])
    else:
        call(["mpv", "--no-terminal", "--ontop", target])

def play(byte):
    path_string = byte.decode("utf8")
    if os.path.exists(path_string):
        print("forwarding to app for playing ", path_string)
        dispatch(path_string)
        return b"success"
    else:
        print("Could not find path ", path_string)
        return b"fail"


class PlayerServer:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.socket = None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.bind((self.host, self.port))
            print("listening on {}:{}".format(self.host, self.port))
            self.socket.listen()
            while True:
                self.serve()
    
    def serve(self):
        conn, addr = self.socket.accept()
        this_data = []
        with conn:
            print("Connected by", addr)
            data = conn.recv(1024)
            if not data:
                return
            length, data = PlayerProtocol.decode(data)
            totalLength = length
            this_data.append(data)
            print("Receive {} bytes".format(len(data)))
            while length - len(data) > 0:
                length -= len(data)
                data = conn.recv(1024)
                print("Receive {} bytes".format(len(data)))
                this_data.append(data)
            this_data = b''.join(this_data)
            print("Receive {} bytes in total".format(len(this_data)))
            assert(len(this_data) == totalLength)
            conn.send(play(this_data))

def main():
    playerServer = PlayerServer()
    playerServer.run()

if __name__ == "__main__":
    main()
