import json
import socket
import threading

import pymongo

from shared.constants import SEGEMENT_1K
from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.constants import LOCALHOST
from shared.constants import log_print
from shared.constants import MONGO_PORT
from shared.protocol import JsonProtocol

class JsonServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((LOCALHOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.log("Listening on {}:{}".format(self.host, self.port))

    def __repr__(self):
        return "{}[{}:{}]".format(self.__class__.__name__, self.host, self.port)

    def __del__(self):
        self.socket.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def log(self, message):
        log_print(str(self), message)

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
                self.log("Connected by {}:{}".format(addr[0], addr[1]))
                data = conn.recv(SEGEMENT_1K)
                if not data:
                    break
                length, data = JsonProtocol.decode(data)
                totalLength = length
                received_data.append(data)
                while length - len(data) > 0:
                    length -= len(data)
                    data = conn.recv(1024)
                    received_data.append(data)
                received_data = b''.join(received_data)
                self.log("Receives {} bytes in total".format(len(received_data)))
                assert(len(received_data) == totalLength)
                msg = json.loads(received_data.decode("utf8"))
                response = self.dispatch(msg)
                conn.send(JsonProtocol.encode(response))

    def dispatch(self, msg):
        pass

    def stop(self):
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()
        self.log("Stop serving.")

class JsonDataServer(JsonServer):

    def __init__(self):
        super().__init__()
        self.client = pymongo.MongoClient(MONGO_PORT) 
        self.log("Connecting to " + MONGO_PORT)
        self.colDict = {}

    def getCollection(self, msg):
        col = self.colDict.get((msg["database"], msg["collection"]))
        if col == None: 
            col = self.client[msg["database"]][msg["collection"]] 
            self.colDict[(msg["database"], msg["collection"])] = col
        return col
    
