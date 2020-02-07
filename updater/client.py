from shared.jsonclient import JsonDataClient

class UpdaterClient(JsonDataClient):

    def update(self, doc_id, query):
        assert(isinstance(query, dict))
        result = self._send({"service" : "update", "doc_id" : doc_id, "query" : query})
        return result

