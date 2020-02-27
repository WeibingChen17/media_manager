import os
import json
import socket
import threading
from bson.objectid import ObjectId

import pymongo

from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.jsonserver import JsonDataServer

class UpdaterServer(JsonDataServer):

    def dispatch(self, msg):
        if msg["service"] == "update":
            return self.update(self.getCollection(msg), msg["doc_id"], msg["query"])
        else:
            return FAIL_CODE

    def update(self, col, doc_id, query):
        query_id = {"_id" : ObjectId(doc_id)}
        for op in query:
            if op == "add":
                for field, value in query[op].items():
                    self.log("Adding  {} : {}".format(field, value))
                    # assume it is an array
                    col.update_one(query_id, {'$push' : {field : value}})
            elif op == "remove":
                for field, value in query[op].items():
                    self.log("Removing  {} : {}".format(field, value))
                    # assume it is an array
                    col.update_one(query_id, {'$pull' : {field : value}})
            elif op == "change":
                for field, value in query[op].items():
                    self.log("Chaning {} : {}".format(field, value))
                    # assume it is not an array
                    col.update_one(query_id, {'$set' : {field : value}})
            elif op == "delete":
                if col.find_one(query_id).get("path"):
                    path = col.find_one(query_id).get("path")
                    if os.path.exists(path):
                        self.log("File {} is deleted".format(path))
                        os.remove(path)
                self.log("Deleting record {}".format(doc_id))
                col.delete_one(query_id)
        # assume happy
        return SUCCEED_CODE

