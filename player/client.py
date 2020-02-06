import os
import socket

from shared.jsonclient import JsonClient
from shared.protocol import SUCCEED_CODE
from shared.protocol import FAIL_CODE

class PlayerClient(JsonClient):

    def play(self, path):
        if not os.path.exists(path):
            return FAIL_CODE
        data = {"reason" : "play", "path" : path}
        return self._send(data)

