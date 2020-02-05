import os
import json
import socket
import threading

from bson.objectid import ObjectId

import pymongo

from shared.protocol import StringProtocol

HOST = "127.0.0.1"

class UpdaterServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.client = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.db = None
        self.col = None
        print("UpdaterServer is listening on {}:{}".format(self.host, self.port))
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
                conn.send(StringProtocol.encode(result.encode("utf8")))

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
        elif data["reason"] == "update":
            return self.update(data["doc_id"], data["query"])
        else:
            return "fail"

    def update(self, doc_id, query):
        query_id = {"_id" : ObjectId(doc_id)}
        for op in query:
            if op == "add":
                for field, value in query[op].items():
                    print("adding  {} : {}".format(field, value))
                    # assume it is an array
                    self.col.update(query_id, {'$push' : {field : value}})
            elif op == "remove":
                for field, value in query[op].items():
                    print("removing  {} : {}".format(field, value))
                    # assume it is an array
                    self.col.update(query_id, {'$pull' : {field : value}})
            elif op == "change":
                for field, value in query[op].items():
                    print("chaning {} : {}".format(field, value))
                    # assume it is not an array
                    self.col.update(query_id, {'$set' : {field : value}})
            elif op == "delete":
                if self.col.find_one(query_id).get("path"):
                    for path in self.col.find_one(query_id).get("path"):
                        if os.path.exists(path):
                            print("File {} is deleted".format(path))
                            os.remove(path)
                print("deleting record {}".format(doc_id))
                self.col.delete_one(query_id)
        # assume happy
        return "succeed"

                    




