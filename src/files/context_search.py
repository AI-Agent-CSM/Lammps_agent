from typing import List

class WeaviateContextSearch:

    def __init__(self, client):
        self.client = client


    def common_neightbourgs(node1, node2):
         common_papers = None
         common_authors = None





    def search(self,query: str, prompt: str, limit: int , collection: str, properties: List[str]):

            reviews = self.client.collections.get(collection)
            response = reviews.query.hybrid(
                query=query,
                query_properties=properties,

                limit=limit
            )
            return response
    

    def  context_search(self,query: str, prompt: str, limit: int, collection: str, properties: List[str]):
         pass