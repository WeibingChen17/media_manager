from shared.jsonclient import JsonDataClient
from shared.protocol import FAIL_CODE
from shared.protocol import MediaEntry

class SearcherClient(JsonDataClient):
    
    def search(self, query):
        if isinstance(query, str):
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

