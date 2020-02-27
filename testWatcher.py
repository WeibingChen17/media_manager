import os
import sys
import time
import shutil
import logging

import pymongo

from watcher.client import WatcherClient
from watcher.server import WatcherServer
from shared.constants import debug_logging

debug_logging()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["testDatabase"]
mycol = mydb["media_manager"]
mycol.delete_many({}) # reset collection

with WatcherServer() as watcherServer:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    watcherClient = WatcherClient(watcherServer)

    watcherClient.set_database("testDatabase", "media_manager")

    tmp_folder = "/tmp/Test2341/"
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.mkdir(tmp_folder)

    with open(tmp_folder + "test1.mp4", 'w') as f:
        f.write("testsjladksfa dfa\n")
        
    with open(tmp_folder + "tet2.jpg", 'w') as f:
        f.write('aldsjfadfjasdf ad\nalkjdlfja')

    watcherClient.watch(tmp_folder)
    time.sleep(0.5)
    assert(mycol.count_documents({}) == 2)

    assert(isinstance(mycol.find_one({"name":"test1.mp4"}).get("path"), str))

    with open(tmp_folder + "test", 'w') as f:
        f.write("tetasdf")

    time.sleep(0.5)
    assert(mycol.count_documents({}) == 2)

    with open(tmp_folder + "test.mp4", 'w' ) as f:
        f.write("dafa\n")

    time.sleep(0.5)
    assert(mycol.count_documents({}) == 3)

    os.rename(tmp_folder + "test.mp4", tmp_folder + "tset3.mp4")
    time.sleep(0.5)
    assert(mycol.count_documents({}) == 3)
    assert(mycol.count_documents({"name":"test.mp4"}) == 0)
    assert(mycol.count_documents({"name":"tset3.mp4"}) == 1)
    assert(mycol.find_one({"name":"tset3.mp4"}).get("path") == tmp_folder + "tset3.mp4")

    os.remove(tmp_folder + "tet2.jpg")
    time.sleep(0.5)
    assert(mycol.count_documents({}) == 2)
    assert(mycol.count_documents({"name":"tet2.jpg"}) == 0)

    # test move
    os.mkdir(tmp_folder + "tmp2/")
    shutil.move(tmp_folder + "tset3.mp4", tmp_folder + "tmp2/tset3.mp4")
    time.sleep(1.5) # very slow, create and delete
    assert(mycol.count_documents({"name":"tset3.mp4"}) == 1)
    assert(mycol.find_one({"name":"tset3.mp4"}).get("path") == tmp_folder + "tmp2/tset3.mp4")

shutil.rmtree(tmp_folder)
mycol.delete_many({}) # reset collection

print("Watcher: Tests pass")
