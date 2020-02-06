import threading
from subprocess import call

from shared.jsonserver import JsonServer
from shared.protocol import SUCCEED_CODE
from shared.protocol import FAIL_CODE
from shared.protocol import LOG_FORMAT

class PlayerServer(JsonServer):

    def dispatch(self, data):
        if data["reason"] == "play":
            return self.play(data["path"])
        else:
            return FAIL_CODE

    def play(self, path):
        self.log("Forwarding to app for playing {} ".format(path))
        thread = threading.Thread(target=self.view, args=(path,))
        thread.start()
        return SUCCEED_CODE

    def view(self, path):
        # exception
        if path.endswith("pdf"):
            call(["evince", path])
        elif path.endswith("jpg") or path.endswith("jpeg") or path.endswith("png") or path.endswith("gif"):
            call(["feh", path])
        else:
            call(["mpv", "--no-terminal", "--ontop", path])
