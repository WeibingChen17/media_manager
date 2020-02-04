import pymogno

from updater.client import UpdaterClient
from updater.server import UpdaterServer

updateServer = updateServer()
updateServer.start()

updateClient = UpdaterClient()
updateClient.set_database("testDatabase")
updateClient.set_collection("media_manager")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["testDatabase"]
mycol = mydb["media_manager"]
mycol.delete_many({}) # reset collection

entry = {"name":["test"], "director":"good"}
mycol.insert_one(entry)

doc_id = mycol.find_one({"name" : "test"}).get("_id")

updateClient.update(doc_id, {"add" : {"name": "test1"}})
assert(mycol.find_one({"name" : "test"}).get("name") == ["test", "test1"])

updateClient.update(doc_id, {"remove" : {"name": "test"}})
assert(mycol.find_one({"name" : "test"}).get("name") == ["test1"])

updateClient.update(doc_id, {"change" : {"director": "bad"}})
assert(mycol.find_one({"name" : "test"}).get("director") == "bad")
