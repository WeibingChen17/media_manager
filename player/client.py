import os
import socket

from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.jsonclient import JsonClient

class PlayerClient(JsonClient):

    def play(self, path):
        if not os.path.exists(path):
            return FAIL_CODE
        data = {"service" : "play", "path" : path}
        return self._send(data)

