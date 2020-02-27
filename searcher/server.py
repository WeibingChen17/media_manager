from bson.objectid import ObjectId

from shared.jsonserver import JsonDataServer

class SearcherServer(JsonDataServer):

    def dispatch(self, msg):
        if msg["service"] == "search":
            return self.search(self.getCollection(msg), msg["query"])
        else:
            return FAIL_CODE

    def search(self, col, query):
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        result = []
        for entry in col.find(query):
            e = dict(entry)
            e["_id"] = str(e["_id"])
            result.append(e)
        return result
        
