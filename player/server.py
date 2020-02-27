import threading
from subprocess import call

from shared.constants import SUCCEED_CODE
from shared.constants import FAIL_CODE
from shared.constants import LOG_FORMAT
from shared.jsonserver import JsonServer

class PlayerServer(JsonServer):

    def dispatch(self, msg):
        if msg["service"] == "play":
            return self.play(msg["path"])
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
