import logging

SEGEMENT_1K = 1024
LOCALHOST = "127.0.0.1"
MEDIA_MANAGER_PORT = 31425
SUCCEED_CODE = {"status" : "succeed"}
FAIL_CODE = {"status" : "fail"}
LOG_FORMAT = "{} - {:<50} - {}"

APP_NAME = "media_manager"
LOG_FILE = "/var/log/media_manager/server.log"
FORMAT = '%(asctime)-15s %(host)-25s %(message)s'

def log_print(host, message):
    logging.info(message, extra={"host": host})

# (todo) merge these two
MEDIA_SUFFIX = [".mp4", ".flv", ".webm", ".jpeg", ".gif", ".png", ".jpg"]
MEDIA_REGEX = [r".*\.mp4", r".*\.flv", r".*\.webm", r".*\.jpeg", r".*\.gif", r".*\.png", r".*\.jpg"]

FIELDS = {
        "path" : "", 
        "md5" : "" , 
        "release_data" : "" , 
        "actress" : [], 
        "director" : "", 
        "maker" : "", 
        "distributor" : "", 
        "rating" : "", 
        "tag" : [], 
        "designation" : "", 
        "name" : [], 
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

    def __repr__(self):
        res = ""
        for field in self.__dict__:
            res += "{:<15} : {}\n".format(field, self.__dict__[field])
        return res

