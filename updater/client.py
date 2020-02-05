import json
import socket

from shared.protocol import StringProtocol

class UpdaterClient:
    def __init__(self, searcherServer=None):
        self.host = None
        self.port = None
        if searcherServer:
            self.host = searcherServer.get_host()
            self.port = searcherServer.get_port()

    def __repr__(self):
        return "UpdateClient[host : {}, port : {}]".format(self.host, self.port)

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def set_database(self, database):
        assert(isinstance(database, str))
        return self._send({"reason" : "set_database", "database" : database})

    def set_collection(self, collection):
        assert(isinstance(collection, str))
        return self._send({"reason" : "set_collection", "collection" : collection})

    def update(self, doc_id, query):
        assert(isinstance(query, dict))
        result = self._send({"reason" : "update", "doc_id" : doc_id, "query" : query})
        # todo : set all response to json format
        # return response["status"]
        return result

    def _send(self, data):
        assert(isinstance(data, dict))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print("UpdaterClient is connnecting to {}:{}".format(self.host, self.port))
        print("Sending json", data)
        s.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, response = StringProtocol.decode(s.recv(1024))
        assert(length == len(response))
        s.close
        return response.decode("utf8")

