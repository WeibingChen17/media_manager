from shared.jsonclient import JsonDataClient

class WatcherClient(JsonDataClient):

    def watch(self, path):
        data = {"service" : "watch", "path": path}
        return self._send(data)

