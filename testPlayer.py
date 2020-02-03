import time
import threading
from player.client import PlayerClient
from player.server import PlayerServer


def main():
    server = PlayerServer()
    server.start()

    client = PlayerClient(server)

    status = client.play("/home/weibing/b.mp4")
    assert(status == "fail")

    time.sleep(1)

    status = client.play("/home/weibing/a.mp4")
    assert(status == "succeed")

    time.sleep(1)

    server.stop()

if __name__ == "__main__":
    main()
