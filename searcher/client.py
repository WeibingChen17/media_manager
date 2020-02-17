from shared.constants import FAIL_CODE
from shared.constants import MediaEntry
from shared.jsonclient import JsonDataClient

def generateRegex(string):
    string = '.*'.join(string.split())
    string = string.replace("-", ".*")
    return ".*" + string + ".*"

class SearcherClient(JsonDataClient):

    def search_by_id(self, entry_id):
        return self.search({"_id" : entry_id})
    
    def search(self, query):
        res = FAIL_CODE
        if isinstance(query, str):
            res = self._send({
                "service" : "search", 
                "query" : {"name" : {"$regex" : generateRegex(query), "$options":"i"}}
                })
        elif isinstance(query, dict):
            if "name" in query:
                query["name"] = {"$regex" : generateRegex(query["name"]), "$options":"i"}
            res = self._send({"service" : "search", "query" : query})
        if res == FAIL_CODE:
            return []
        else:
            return [MediaEntry(entry) for entry in res]

