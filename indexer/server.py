import os
import socket
import json
import threading
import hashlib

import pymongo
import filetype

from shared.protocol import StringProtocol

HOST = "127.0.0.1"

class IndexerServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind((HOST, 0))
        self.host, self.port = self.socket.getsockname()
        self.client = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.db = None
        self.col = None
        print("IndexerServer is listening on {}:{}".format(self.host, self.port))
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
                status = self.dispatch(received_data)
                conn.send(StringProtocol.encode(status.encode("utf8")))

    def stop(self):
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()

    def dispatch(self, byte):
        data = json.loads(byte.decode("utf8"))
        if data["type"] == "folder":
            return self.index_folder(data["path"])
        elif data["type"] == "database":
            return self.set_database(data["path"])
        elif data["type"] == "collection":
            return self.set_collection(data["path"])
        elif data["type"].startswith("file"):
            reason = data["type"].split("_")[-1]
            return self.index_file(data["path"], reason, dest_path=data["dest_path"])
        else:
            return "fail"

    def index_file(self, file_path, reason, dest_path=""):
        path_query = {"path": file_path}
        if reason == "create":
            if self.col.count_documents(path_query) > 0:
                print("Ignore an existing file path")
                return "succeed"
            md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            md5_query =  {"md5": md5}
            doc = self.col.find(md5_query)
            if self.col.count_documents(md5_query) == 0:
                # unique new file: create a new doc
                entry = dict()
                entry["path"] = [file_path]
                entry["md5"] = hashlib.md5(open(file_path,'rb').read()).hexdigest()
                entry["release date"] = ""
                entry["actress"] = []
                entry["director"] = ""
                entry["maker"] = ""
                entry["disttributor"] = ""
                entry["rating"] = "0"
                entry["tag"] = []
                entry["designation"] = ""
                # add size and duration
                entry["name"] = [os.path.basename(file_path)]
                entry["size"] = os.path.stat(file_path).st_size
                entry["type"] = filetype.guess(file_path)
                # todo: determine the best way of determinnig duration(ffprob)
                entry["duration"] = ""
                self.col.insert_one(entry)
            else:
                # the same file: append the path
                self.col.update(md5_query, {'$push': {"path" : file_path}})
            return "succeed"
        elif reason == "move":
            if self.col.count_documents(path_query) == 0:
                print("Ignore nonexisting file path")
                return "succeed"
            self.col.update(path_query, {
                '$push': {"path" : dest_path}, 
                '$push', {"name": os.path.basename(dest_path)}
                })
            self.col.update(path_query, {
                '$pull': {"path" : file_path}
                '$pull': {"name" : os.path.basename(file_path)}
                })
            return "succeed"
        elif reason == "delete":
            if self.col.count_documents(path_query) == 0:
                print("Ignore nonexisting file path")
                return "succeed"
            self.col.update(path_query, {'$pull': {"path" : file_path}})
            self.col.delete_many({"path" : []})
            return "succeed"
        else:
            return "fail"

    def index_folder(self, folder_path):
        for dirpath, _, names in os.walk(folder_path):
            for name in names:
                self.index_file(os.path.join(dirpath, name), "create")
        return "succeed"
