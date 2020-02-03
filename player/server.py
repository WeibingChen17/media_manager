import socket
import threading
import os
from subprocess import call

from shared.protocol import StringProtocol

HOST = "127.0.0.1"

# will be replaced by another server
def dispatch(path):
    target = path
    if target.endswith("pdf"):
        call(["evince", target])
    elif target.endswith("jpg") or target.endswith("jpeg") or target.endswith("png") or target.endswith("gif"):
        call(["feh", target])
    else:
        call(["mpv", "--no-terminal", "--ontop", target])

# will be replaced by another server
def play(byte):
    path = byte.decode("utf8")
    if os.path.exists(path):
        print("forwarding to app for playing ", path)
        thread = threading.Thread(target=dispatch, args=(path,))
        thread.start()
        return b"succeed"
    else:
        print("Could not find path", path)
        return b"fail"

class PlayerServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        print("PlayerServer is listening on {}:{}".format(self.host, self.port))

    def __del__(self):
        self.socket.close()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def start(self):
        self.thread = threading.Thread(target=self.__run, args=())
        self.thread.start()

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
                status = play(received_data)
                conn.send(StringProtocol.encode(status))

    def stop(self):
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()

