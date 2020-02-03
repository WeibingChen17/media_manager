from searcher.client import SearcherClient
from searcher.server import SearcherServer

searcherServer = SearcherServer()
searcherServer.start()

searcherClient = SearcherClient(searcherServer)

# default match name
result = searcherClient.search("test")
assert(len(result) == 0)

# insert a data
# insert test, tag: good

result = searcherClient.search("test")
assert(len(result) == 1)
assert(result[0]["name"] == "test")

# insert another data
# insert test2, tag: bad

result = searcherClient.search("test")
assert(len(result) == 2)
assert(result[0]["name"] == "test")


result = searcherClient.search({"tag" : "good"})
assert(len(result) == 1)
assert(result[0]["tag"] == "good")


searcherServer.stop()
