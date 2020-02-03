import os
import time
import shutil

import pymongo

from indexer.client import IndexerClient
from indexer.server import IndexerServer
from watcher.client import MediaWatcherClient
from watcher.server import MediaWatcherServer

indexerServer = IndexerServer()
indexerServer.start()

indexerClient = IndexerClient(indexerServer)
indexerClient.set_database("testDatabase")
indexerClient.set_collection("media_manager")

mediaWatcherServer = MediaWatcherServer()
mediaWatcherServer.start()

mediaWatcherClient = MediaWatcherClient(mediaWatcherServer)
mediaWatcherClient.set_indexer(indexerClient)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["testDatabase"]
mycol = mydb["media_manager"]
mycol.delete_many({}) # reset collection

test_path = "/tmp/ssdf234/"
if os.path.exists(test_path):
    shutil.rmtree(test_path)
os.mkdir(test_path)

mediaWatcherClient.watch(test_path)

with open(test_path + "tmp.jpg", 'w') as f:
    f.write("tests \n")

with open(test_path + "tmp1.mp4", 'w') as f:
    f.write("tests 3\n")

time.sleep(1)
# assert
myquery = { "path": { "$regex": "^" + test_path }}
mydoc = mycol.find(myquery)
for x in mydoc:
    print(dict(x))
assert(mycol.count_documents(myquery) == 2)

os.remove(test_path + "tmp1.mp4")
time.sleep(1)
mydoc = mycol.find(myquery)
assert(mycol.count_documents(myquery) == 1)

mediaWatcherServer.stop()
indexerServer.stop()
