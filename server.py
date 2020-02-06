from player.server import PlayerServer
from updater.server import UpdaterServer
from searcher.server import SearcherServer
from watcher.server import WatcherServer

class MediaManagerServer:
    HOST = 127.0.0.1
    PORT = 31425
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.bind(HOST, PORT)
        self.watcherServer = watcherServer()
        self.playerServer = PlayerServer()
        self.searcherServer = SearcherServer()
        self.updaterServer = UpdaterServer()

        self.watcherServer.start()
        self.playerServer.start()
        self.searcherServer.start()
        self.updaterServer.start()

    def __del__(self)
        self.watcherServer.stop()
        self.playerServer.stop()
        self.searcherServer.stop()
        self.updaterServer.stop()

    def start(self):
        self.thread = threading.Thread(target=self.__run, args=())
        self.thread.start()

    def __run(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.socket.listen()
            conn, addr = self.socket.accept()
            received_data = []
            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                if not data:
                    break
                length, data = StringProtocol.decode(data)
                totalLength = length
                received_data.append(data)
                print("Receive {} bytes".format(len(data)))
                while length - len(data) > 0:
                    length -= len(data)
                    data = conn.recv(1024)
                    print("Receive {} bytes".format(len(data)))
                    received_data.append(data)
                received_data = b''.join(received_data)
                print("Receive {} bytes in total".format(len(received_data)))
                assert(len(received_data) == totalLength)
                result = self.dispatch(received_data) 
                conn.send(StringProtocol.encode(result.encode("utf8")))

    def stop(self):
        self.thread.do_run = False
        ending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ending_socket.connect((self.host, self.port))
        ending_socket.close()
        self.thread.join()

    def dispatch(self):
        pass
