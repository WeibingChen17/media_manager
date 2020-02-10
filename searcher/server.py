from bson.objectid import ObjectId

from shared.jsonserver import JsonDataServer

class SearcherServer(JsonDataServer):

    def dispatch(self, data):
        if data["service"] == "search":
            return self.search(data["query"])
        else:
            return FAIL_CODE

    def search(self, query):
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        result = []
        for entry in self.col.find(query):
            e = dict(entry)
            e["_id"] = str(e["_id"])
            result.append(e)
        return result
        
