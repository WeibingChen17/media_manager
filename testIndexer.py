import os
import shutil

import pymongo

from indexer.client import IndexerClient
from indexer.server import IndexerServer

indexerServer = IndexerServer()
indexerServer.start()

indexerClient = IndexerClient(indexerServer)
indexerClient.set_database("testDatabase")
indexerClient.set_collection("media_manager")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["testDatabase"]
mycol = mydb["media_manager"]
mycol.delete_many({}) # reset collection

test_path = "/tmp/ssdf234/"
if os.path.exists(test_path):
    shutil.rmtree(test_path)
os.mkdir(test_path)

with open(test_path + "tmp", 'w') as f:
    f.write("tests \n")

with open(test_path + "tmp1", 'w') as f:
    f.write("tests 3\n")

status = indexerClient.index_folder(test_path)
print(status)
assert(status == "succeed")

# assert
myquery = { "path": { "$regex": "^" + test_path }}
mydoc = mycol.find(myquery)
for x in mydoc:
    print(dict(x))
assert(mycol.count_documents(myquery) == 2)

with open(test_path + "tmp2", 'w') as f:
    f.write("tests 2\n")

indexerClient.index_file(test_path+"tmp2", "create")

# assert
myquery = { "path": test_path+"tmp2"}
assert(mycol.count_documents(myquery) == 1)

os.rename(test_path+"tmp2", test_path+"tmp3")
indexerClient.index_file(test_path+"tmp2", "move", test_path+"tmp3")
myquery = { "path": test_path+"tmp3"}
mydoc = mycol.find(myquery)
for x in mydoc:
    print(dict(x))
assert(mycol.count_documents(myquery) == 1)

os.remove(test_path+"tmp3")
indexerClient.index_file(test_path+"tmp3", "delete")
myquery = { "path": test_path+"tmp3"}
mydoc = mycol.find(myquery)
assert(mycol.count_documents(myquery) == 0)

with open(test_path + "tmp4", 'w') as f:
    f.write("tests \n")
indexerClient.index_file(test_path+"tmp4", "create")
myquery = { "path": test_path+"tmp4"}
mydoc = mycol.find(myquery)
assert(mycol.count_documents(myquery) == 1)
for x in mydoc:
    print(x)
    assert(len(x["path"]) == 2)

status = indexerClient.index_folder(test_path)

indexerServer.stop()
