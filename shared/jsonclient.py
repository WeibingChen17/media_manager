import json
import socket 
from datetime import datetime

from shared.constants import log_print
from shared.constants import SEGEMENT_1K
from shared.constants import LOCALHOST
from shared.protocol import JsonProtocol

class JsonClient:
    def __init__(self, json_server=None):
        self.host = LOCALHOST
        self.port = None
        if json_server:
            self.host = json_server.get_host()
            self.port = json_server.get_port()

    def __repr__(self):
        return "{}[server: {}:{}]".format(self.__class__.__name__, self.host, self.port)

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def log(self, message):
        log_print(str(self), message)

    def _send(self, data, wait_for_replay=True):
        assert(isinstance(data, dict))
        self._add_context(data)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.log("Connecting to server.")
        self.log("Sending {}".format(data))
        s.sendall(JsonProtocol.encode(data)) 
        if wait_for_replay:
            length, data = JsonProtocol.decode(s.recv(SEGEMENT_1K))
            totalLength = length
            received_data = [data]
            while length - len(data):
                length -= len(data)
                data = s.recv(SEGEMENT_1K)
                received_data.append(data)
            received_data = b''.join(received_data)
            self.log("Receives {} bytes in total".format(len(received_data)))
            assert(len(received_data) == totalLength)
            s.close()
            return json.loads(received_data.decode("utf8"))
        s.close()

    def _add_context(self, data):
        pass

class JsonDataClient(JsonClient):
    
    def __init__(self, json_server=None):
        super().__init__(json_server)
        self.db = None
        self.col = None

    def set_database(self, database, collection):
        assert(isinstance(database, str))
        assert(isinstance(collection, str))
        self.db = database
        self.col = collection

    def _add_context(self, data):
        data.update({"database": self.db, "collection": self.col})

