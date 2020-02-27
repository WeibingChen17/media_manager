from shared.jsonclient import JsonDataClient

class WatcherClient(JsonDataClient):

    def watch(self, path, force_scan=False):
        data = {"service": "watch", "path": path, "force_scan": force_scan}
        return self._send(data, wait_for_replay=False)
    
    def unwatch(self, path):
        data = {"service": "unwatch", "path": path}
        # wait_for_replay = true?
        return self._send(data, wait_for_replay=False)

