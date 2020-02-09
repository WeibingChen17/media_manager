import json
import collections
from datetime import datetime

SEGEMENT_1K = 1024
LOCALHOST = "127.0.0.1"
MEDIA_MANAGER_PORT = 31425
SUCCEED_CODE = {"status" : "succeed"}
FAIL_CODE = {"status" : "fail"}
LOG_FORMAT = "{} - {:<50} - {}"

# (todo) merge these two
MEDIA_SUFFIX = [".mp4", ".flv", ".webm", ".jpeg", ".gif", ".png", ".jpg"]
MEDIA_REGEX = [r".*\.mp4", r".*\.flv", r".*\.webm", r".*\.jpeg", r".*\.gif", r".*\.png", r".*\.jpg"]

def log_print(host, string):
    print(LOG_FORMAT.format(datetime.now(), host, string))

FIELDS = {
        "path" : "", 
        "md5" : "" , 
        "release_data" : "" , 
        "actress" : [], 
        "director" : "", 
        "maker" : "", 
        "distributor" : "", 
        "rating" : "", 
        "tag" : "", 
        "designation" : "", 
        "name" : "", 
        "size" : "", 
        "type" : "", 
        "duration" : ""
        }

class MediaEntry:
    def __init__(self, entry=None):
        if entry:
            self.__dict__ = dict(entry)
        else:
            self.__dict__ = FIELDS
    
    def asdict(self):
        return dict(self.__dict__)


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

