import json
import socket

from shared.protocol import StringProtocol

class SearcherClient:
    def __init__(self, searcherServer=None):
        self.host = None
        self.port = None
        if searcherServer:
            self.host = searcherServer.get_host()
            self.port = searcherServer.get_port()

    def __repr__(self):
        return "SearcherClient[host : {}, port : {}]".format(self.host, self.port)

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

    def search(self, query):
        if isinstance(query, str):
            result = self._send({
                "reason" : "search", 
                "query" : {"name" : {"$regex" : ".*" + query + ".*"}}
                })
        elif isinstance(query, dict):
            if "name" in query:
                query["name"] = {"$regex" : ".*" + query["name"] + ".*"}
            result = self._send({"reason" : "search", "query" : query})
        return json.loads(result)

    def _send(self, data):
        assert(isinstance(data, dict))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print("SearcherClient is connnecting to {}:{}".format(self.host, self.port))
        print("Sending json", data)
        s.sendall(StringProtocol.encode(json.dumps(data).encode("utf8")))
        length, response = StringProtocol.decode(s.recv(1024))
        assert(length == len(response))
        s.close
        return response.decode("utf8")

