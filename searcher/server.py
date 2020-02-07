from shared.jsonserver import JsonDataServer

class SearcherServer(JsonDataServer):

    def dispatch(self, data):
        if data["service"] == "search":
            return self.search(data["query"])
        else:
            return FAIL_CODE

    def search(self, query):
        result = []
        for entry in self.col.find(query):
            e = dict(entry)
            e["_id"] = str(e["_id"])
            result.append(e)
        return result
        
