import json
import socket
import threading

import pymongo

from shared.protocol import SEGEMENT_1K
from shared.protocol import SUCCEED_CODE
from shared.protocol import FAIL_CODE
from shared.protocol import LOCALHOST
from shared.protocol import log_print
from shared.protocol import JsonProtocol

MONGO_PORT = "mongodb://localhost:27017/"

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

    def log(self, string):
        log_print(str(self), string)

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
                received_json = json.loads(received_data.decode("utf8"))
                preresponse = self.predispatch(received_json)
                response = preresponse if preresponse else self.dispatch(received_json)
                conn.send(JsonProtocol.encode(response))

    def predispatch(self, received_json):
        return None

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
        self.db = None
        self.col = None
        self.log("Connecting to " + MONGO_PORT)
    
    def get_database(self):
        return self.db

    def get_collection(self):
        return self.col

    def set_database(self, database):
        self.db = self.client[database]
        self.log("Uses Database {}".format(database))
        return SUCCEED_CODE

    def set_collection(self, collection):
        if not self.db:
            raise Exception("No database is selected yet")
        self.col = self.db[collection]
        self.log("Uses Collection {}".format(collection))
        return SUCCEED_CODE

    def predispatch(self, data):
        if data["service"] == "set_database":
            return self.set_database(data["database"])
        elif data["service"] == "set_collection":
            return self.set_collection(data["collection"])
        return None

