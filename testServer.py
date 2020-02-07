from subprocess import call

from shared.jsonclient import JsonClient

class TestClient(JsonClient):

    def query(self, server_name):
        return self._send({"service" : "GetServer", "server_name" : server_name})

testClient = TestClient()
testClient.set_port(31425)

call(["./server.py", "start"])
print("Player is at : ", testClient.query("Player"))
print("Searcher is at : ", testClient.query("Searcher"))
print("Watcher is at : ", testClient.query("Watcher"))
print("Updater is at : ", testClient.query("Updater"))
print("Nothing is at : ", testClient.query("Nothing"))

call(["./server.py", "stop"])
try:
    print("Player is at : ", testClient.query("Player"))
except ConnectionRefusedError:
    pass
