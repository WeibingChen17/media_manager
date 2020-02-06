import json
from datetime import datetime

SEGEMENT_1K = 1024
LOCALHOST = "127.0.0.1"
SUCCEED_CODE = {"status" : "succeed"}
FAIL_CODE = {"status" : "fail"}
LOG_FORMAT = "{} {:<40} - {}"

def log_print(host, string):
    print(LOG_FORMAT.format(datetime.now(), host, string))

class JsonProtocol:
    def __init__(self):
        pass

    @staticmethod
    def encode(data):
        assert(isinstance(data, dict))
        bytestring = json.dumps(data).encode("utf8")
        length = len(bytestring)
        return (length).to_bytes(4, byteorder="little", signed=False) + bytestring

    @staticmethod
    def decode(byte):
        assert(isinstance(byte, bytes))
        length = int.from_bytes(byte[:4], byteorder="little", signed=False)
        return length, byte[4:]

