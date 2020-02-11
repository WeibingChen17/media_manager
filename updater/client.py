from shared.protocol import SUCCEED_CODE
from shared.jsonclient import JsonDataClient

class UpdaterClient(JsonDataClient):

    def delete(self, doc_id):
        query = {"delete" : {}}
        return self.update(doc_id, query)

    def update(self, doc_id, query):
        assert(isinstance(query, dict))
        result = self._send({"service" : "update", "doc_id" : doc_id, "query" : query})
        return result

    def update_all(self, doc_id, queryList):
        assert(isinstance(queryList, list))
        fail_state = False
        for query in queryList:
            status = self.update(doc_id, query)
            if status != SUCCEED_CODE:
                print("Fail in {}".format(query))
                fail_state = True
        return SUCCEED_CODE if not fail_state else FAIL_CODE

