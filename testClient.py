import os 
import shutil

import pymongo

from client import MediaManagerClient

test_database = "testDatabase"
test_collection = "media_manager"
test_path = "/tmp/Test1234/"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[test_database]
mycol = mydb[test_collection]
mycol.delete_many({}) # reset collection

# build watch foldre
if os.path.exists(test_path):
    shutil.rmtree(test_path)
os.mkdir(test_path)

with open(test_path + "test1.mp4", 'w') as f:
    f.write("testsjladksfa dfa\n")
    
with open(test_path + "test2.jpg", 'w') as f:
        f.write('aldsjfadfjasdf ad\nalkjdlfja')

shutil.copyfile("/home/weibing/a.mp4", test_path + "test2\ d.mp4")

with open(test_path + "test", 'w') as f:
    f.write("tetasdf")

with open(test_path + "large_test.mp4", 'wb') as f:
    f.seek(1073741824-1)
    f.write(b"\0")

# run
try:
    mediaManagerClient = MediaManagerClient()
    mediaManagerClient.set_database(test_database)
    mediaManagerClient.set_collection(test_collection)
    mediaManagerClient.set_watch_folders([test_path])

    mediaManagerClient.run()
finally:
    shutil.rmtree(test_path)
