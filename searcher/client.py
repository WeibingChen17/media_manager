from shared.jsonclient import JsonDataClient
from shared.protocol import FAIL_CODE

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
        return res if res != FAIL_CODE else []

