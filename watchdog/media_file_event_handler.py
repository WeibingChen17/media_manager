from watchdog.events import RegexMatchingEventHandler

class MediaFileEventHandler(RegexMatchingEventHandler):
    MEDIA_REGEX = [r".*\.mp4", r".*\.flv", r".*\.webm", r".*\.jpeg", r".*\.gif", r".*\.png", r".*\.jpg"]

    def __init__(self):
        super().__init__(self.MEDIA_REGEX)

    def on_created(self, event):
        print("file {} is created".format(event.src_path))

    def on_moved(self, event):
        print("file {} is moved".format(event.src_path))

    def on_deleted(self, event):
        print("file {} is deleted".format(event.src_path))

    def on_modified(self, event):
        print("file {} is modified".format(event.src_path))


