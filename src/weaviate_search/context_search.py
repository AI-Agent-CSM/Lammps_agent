from typing import List
import weaviate.classes as wvc
class WeaviateContextSearch:

    def __init__(self, client):
        self.client = client


    def common_neightbourgs(self,node1_uuid, node2_uuid, collection: str, reference_property:str):
         col = self.client.collections.get(collection)

         obj = col.query.fetch_object_by_id(node1_uuid,
                return_references=[
                wvc.query.QueryReference(
                link_on=reference_property,
                return_properties=["title"]
                )])
         obj2 = col.query.fetch_object_by_id(node2_uuid,   return_references=[
                wvc.query.QueryReference(
                link_on=reference_property,
                return_properties=["title"]
                )])
         
         intersection = set(obj.references[reference_property].objects).intersection(set(obj2.references[reference_property].objects))


         return intersection 
    

    def fetch_references_with_decay(self, collection, uuid, reference_property, depth, current_depth=1, decay_factor=0.5):
        if depth == 0:
            return set()
        
        col = self.client.collections.get(collection)
        obj = col.query.fetch_object_by_id(uuid, return_references=[
            wvc.query.QueryReference(
                link_on=reference_property,
                return_properties=["uuid"]  # Assuming uuid is the property to uniquely identify objects
            )
        ])
        
        # Apply decay based on the current depth
        references = set([(ref.uuid, decay_factor ** (current_depth-1)) for ref in obj.references[reference_property].objects])
        
        if current_depth < depth:
            for ref_uuid, _ in references.copy():  # Use copy to avoid modifying the set while iterating
                deeper_references = self.fetch_references_with_decay(collection, ref_uuid, reference_property, depth, current_depth + 1, decay_factor)
                # Merge with existing references, summing decayed values for duplicates
                for deeper_ref, deeper_decay in deeper_references:
                    if any(deeper_ref == ref for ref, _ in references):
                        references = {(ref, decay + deeper_decay) if ref == deeper_ref else (ref, decay) for ref, decay in references}
                    else:
                        references.add((deeper_ref, deeper_decay))
        
        return references

    def jaccard_score_with_decay(self, node1_uuid, node2_uuid, collection: str, reference_property: str, depth: int, decay_factor=0.5):
        references_node1 = self.fetch_references_with_decay(collection, node1_uuid, reference_property, depth, decay_factor=decay_factor)
        references_node2 = self.fetch_references_with_decay(collection, node2_uuid, reference_property, depth, decay_factor=decay_factor)
        
        # Convert to dictionary for easy access to decay values
        references_node1_dict = dict(references_node1)
        references_node2_dict = dict(references_node2)
        
        intersection_keys = set(references_node1_dict.keys()).intersection(set(references_node2_dict.keys()))
        union_keys = set(references_node1_dict.keys()) | set(references_node2_dict.keys())
        
        # Sum of decay values for intersection and union
        intersection_score = sum(min(references_node1_dict[k], references_node2_dict[k]) for k in intersection_keys)
        union_score = sum(references_node1_dict.get(k, 0) + references_node2_dict.get(k, 0) - min(references_node1_dict.get(k, 0), references_node2_dict.get(k, 0)) for k in union_keys)
        
        if union_score == 0:  # Avoid division by zero
            return 0, set()
        
        return (intersection_score / union_score, intersection_keys)
    


    def jaccard_score_with_decay(self, node1_uuid, node2_uuid, collection: str, reference_property: str, depth: int, decay_factor=0.5):
        references_node1 = self.fetch_references_with_decay(collection, node1_uuid, reference_property, depth, decay_factor=decay_factor)
        references_node2 = self.fetch_references_with_decay(collection, node2_uuid, reference_property, depth, decay_factor=decay_factor)




    def search(self,query: str, limit: int , collection: str, properties: List[str], depth, score_threshold):

            reviews = self.client.collections.get(collection)
            response = reviews.query.hybrid(
                query=query,
                query_properties=properties,
                return_references=[
                wvc.query.QueryReference(
                link_on="hasReferencedPaper",
                return_properties=["title"]
                )],
                limit=limit
            )

            # calculate jaccard score between responses
            correlated = []

            for i in response:
                for j in response:
                    if i.id != j.id:
                        score, intersection = self.jaccard_score(i.id, j.id, collection,depth, "hasReferencedPaper")
                        if score > score_threshold:
                             correlated.append((score, i)) 


            

            correlated.sort(key=lambda x: x[0], reverse=True)   

    def  context_search(self,query: str, reference: str, limit: int, collection: str, properties: List[str], references_properties: List[str]):
            reviews = self.client.collections.get(collection)
            response = reviews.query.hybrid(
                query=query,
                return_references=[
                wvc.query.QueryReference(
                link_on=reference,
                return_properties=["uuid"]
                )],
                limit=limit
            )

            result = {}
            properties = []
            references_objects= []
            for obj in response.objects:
                 properties.append(obj.properties)
                 obj_ref = []
                 for ref_obj in obj.references[reference].objects:
                      obj_ref.append(ref_obj.properties)
                 references_objects.append(obj_ref)


            result["properties"] = properties
            result["references"] = references_objects
            
            return result
