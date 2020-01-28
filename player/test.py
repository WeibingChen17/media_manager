import time
from client import PlayerClient
from server import PlayerServer
import threading

server = PlayerServer()
server.start()

client = PlayerClient(server.get_host(), server.get_port())

status = client.play("/home/weibing/b.mp4")
assert(status == "fail")

time.sleep(1)

status = client.play("/home/weibing/a.mp4")
assert(status == "succeed")

time.sleep(1)

server.stop()
