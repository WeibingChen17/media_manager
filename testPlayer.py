import time
from player.client import PlayerClient
from player.server import PlayerServer


def main():
    with PlayerServer() as server:
        client = PlayerClient(server)

        response = client.play("/home/weibing/b.mp4")
        assert(response["status"] == "fail")

        time.sleep(1)

        response = client.play("/home/weibing/a.mp4")
        assert(response["status"] == "succeed")


if __name__ == "__main__":
    main()
    print("Player: Tests pass")
