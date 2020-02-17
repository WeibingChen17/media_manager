from shared.constants import FAIL_CODE
from shared.constants import MediaEntry
from shared.jsonclient import JsonDataClient

class SearcherClient(JsonDataClient):

    def search_by_id(self, entry_id):
        return self.search({"_id" : entry_id})
    
    def search(self, query):
        if isinstance(query, str):
            query = query.replace("-", ".*")
            res =  self._send({
                "service" : "search", 
                "query" : {"name" : {"$regex" : ".*" + query + ".*"}}
                })
        elif isinstance(query, dict):
            if "name" in query:
                query["name"] = {"$regex" : ".*" + query["name"] + ".*"}
            res =  self._send({"service" : "search", "query" : query})
        if res == FAIL_CODE:
            return []
        else:
            return [MediaEntry(entry) for entry in res]

