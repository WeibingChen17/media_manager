import os
import shutil

import pymongo

from searcher.client import SearcherClient
from searcher.server import SearcherServer

with SearcherServer() as searcherServer:

    searcherClient = SearcherClient(searcherServer)
    searcherClient.set_database("testDatabase")
    searcherClient.set_collection("media_manager")

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["testDatabase"]
    mycol = mydb["media_manager"]
    mycol.delete_many({}) # reset collection

    # default match name
    result = searcherClient.search("test")
    assert(len(result) == 0)

    # insert a data
    # insert test, tag: good
    entry = {"name":"test", "tag": ["good"]}
    mycol.insert_one(entry)

    result = searcherClient.search("test")
    assert(len(result) == 1)
    assert(result[0].name == "test")

    # insert another data
    # insert test2, tag: bad
    entry = {"name":"test2", "tag": ["bad"]}
    mycol.insert_one(entry)

    result = searcherClient.search("test")
    assert(len(result) == 2)
    assert(result[0].name == "test")

    result = searcherClient.search({"tag" : "good"})
    assert(len(result) == 1)
    assert(result[0].tag == ["good"])


