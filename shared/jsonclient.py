import json
import socket 
from datetime import datetime

from shared.protocol import SEGEMENT_1K
from shared.protocol import log_print
from shared.protocol import JsonProtocol

class JsonClient:
    def __init__(self, json_server=None):
        self.host = None
        self.port = None
        if json_server:
            self.host = json_server.get_host()
            self.port = json_server.get_port()

    def log(self, string):
        log_print(str(self), string)

    def __repr__(self):
        return "{}[server: {}:{}]".format(self.__class__.__name__, self.host, self.port)

    def set_host(self, host):
        self.host = host

    def set_prot(self, port):
        self.port = port

    def _send(self, data):
        assert(isinstance(data, dict))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.log("Connecting to server.")
        self.log("Sending {}".format(data))
        s.sendall(JsonProtocol.encode(data)) 
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
