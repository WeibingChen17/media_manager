import os
import time
import shutil

from watcher.client import MediaWatcherClient
from watcher.server import MediaWatcherServer

mediaWatcherServer = MediaWatcherServer()
mediaWatcherServer.start()

mediaWatcherClient = MediaWatcherClient(mediaWatcherServer)

tmp_folder = "/tmp/Test2341"
if not os.path.exists(tmp_folder):
    os.mkdir(tmp_folder)

mediaWatcherClient.watch(tmp_folder)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

shutil.rmtree(tmp_folder)
mediaWatcherServer.stop()
