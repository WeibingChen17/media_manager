from shared.jsonclient import JsonDataClient

class UpdaterClient(JsonDataClient):

    def delete(self, doc_id):
        query = {"delete" : {}}
        return self.update(doc_id, query)

    def update(self, doc_id, query):
        assert(isinstance(query, dict))
        result = self._send({"service" : "update", "doc_id" : doc_id, "query" : query})
        return result

