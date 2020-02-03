import os
import json
import socket

from indexer.protocol import StringProtocol

class IndexerClient:
    def __init__(self, indexerServer=None):
        if indexerServer:
            self.host = indexerServer.get_host()
            self.port = indexerServer.get_port()
    
    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def __del__(self):
        self.socket.close()

    def set_database(self, database):
        return self._send_to_server(database, "database")

    def set_collection(self, collection):
        return self._send_to_server(collection, "collection")

    def index_folder(self, folder):
        if not os.path.exists(folder):
            raise Exception("Cannot find foldder")
        return self._send_to_server(folder, "folder")

    def index_file(self, file_path, reason, dest_path=""):
        if reason == "create" and not os.path.exists(file_path):
            raise Exception("Cannot find file")
        if reason == "move" and not dest_path:
            raise Exception("dest path missed")
        if dest_path and not os.path.exists(dest_path):
            raise Exception("dest path does not exisit")
        return self._send_to_server(file_path, "file" + "_" + reason, dest_path)

    def _send_to_server(self, path, path_type, dest_path=""):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("IndexerClient is connecting to {}:{}".format(self.host, self.port))
        print("Sending ", path)
        data = {"type" : path_type, "path" : path, "dest_path" : dest_path}
        self.socket.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, status = StringProtocol.decode(self.socket.recv(1024))
        assert(length == len(status))
        self.socket.close()
        return status.decode("utf8")

