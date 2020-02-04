import json
import socket
import threading

import pymongo

from shared.protocol import StringProtocol

HOST = "127.0.0.1"

class SearcherServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.client = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.db = None
        self.col = None
        print("SearcherServer is listening on {}:{}".format(self.host, self.port))
        print("Connect to mongodb://localhost:27017/")
        print("Database: None")
        print("Collection: None")

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_database(self):
        return self.db

    def get_collection(self):
        return self.col

    def set_database(self, database):
        self.db = self.client[database]
        print("Use Database {}".format(database))
        return "succeed"

    def set_collection(self, collection):
        if not self.db:
            raise Exception("No database is selected yet")
        self.col = self.db[collection]
        print("Use Collection {}".format(collection))
        return "succeed"

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
                result = self.dispatch(received_data) 
                conn.send(StringProtocol.encode(json.dumps(result).encode("utf8")))

    def stop(self):
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()

    def dispatch(self, received_data):
        data = json.loads(received_data.decode("utf8"))
        if data["reason"] == "set_database":
            return self.set_database(data["database"])
        elif data["reason"] == "set_collection":
            return self.set_collection(data["collection"])
        elif data["reason"] == "search":
            return self.search(data["query"])
        else:
            return "fail"

    def search(self, query):
        result = []
        for entry in self.col.find(query, {'_id': 0}):
            result.append(dict(entry))
        return result
        
