import collections
import json

class JsonProtocol:
    def __init__(self):
        pass

    @staticmethod
    def encode(data):
        try:
            bytestring = json.dumps(data).encode("utf8")
            length = len(bytestring)
            return (length).to_bytes(4, byteorder="little", signed=False) + bytestring
        except:
            print("Fail to encode input " + data)

    @staticmethod
    def decode(byte):
        assert(isinstance(byte, bytes))
        length = int.from_bytes(byte[:4], byteorder="little", signed=False)
        return length, byte[4:]

