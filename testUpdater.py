import pymongo

from updater.client import UpdaterClient
from updater.server import UpdaterServer

with UpdaterServer() as updaterServer:

    updaterClient = UpdaterClient(updaterServer)
    updaterClient.set_database("testDatabase")
    updaterClient.set_collection("media_manager")

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["testDatabase"]
    mycol = mydb["media_manager"]
    mycol.delete_many({}) # reset collection

    entry = {"name":["test"], "director":"good"}
    mycol.insert_one(entry)

    doc_id = str(mycol.find_one({"name" : "test"}).get("_id"))

    updaterClient.update(doc_id, {"add" : {"name": "test1"}})
    assert(mycol.find_one({"name" : "test"}).get("name") == ["test", "test1"])

    updaterClient.update(doc_id, {"remove" : {"name": "test"}})
    assert(mycol.find_one({"name" : "test1"}).get("name") == ["test1"])

    updaterClient.update(doc_id, {"change" : {"director": "bad"}})
    assert(mycol.find_one({"name" : "test1"}).get("director") == "bad")

    updaterClient.update(doc_id, {"change" : {"director": "good"}, "add" : { "name": "test2"}})
    assert(mycol.find_one({"name" : "test1"}).get("director") == "good")
    assert(mycol.find_one({"name" : "test2"}).get("name") == ["test1", "test2"])

    updaterClient.update(doc_id, {"delete" : {}})
    assert(mycol.count_documents({"name" : "test1"}) == 0)

print("Tests pass")
