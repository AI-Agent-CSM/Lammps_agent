import weaviate
from weaviate.classes.config import Property, DataType, ReferenceProperty
import weaviate.classes as wvc
import argparse
import uuid
import os
from ..weaviate_search.tei import TEI
#  this is a file for ingesting XML Scientific data into Weaviate
# By using a tools like Grobib for converting pdfs to XML/TEI format
# to search in a smart way scientific papers.

def common_neightbourgs(node1, node2):

    """Find common neighbours between two nodes"""
    neighbours1 = node1.neighbours
    neighbours2 = node2.neighbours
    common_neighbours = [n for n in neighbours1 if n in neighbours2]
    return common_neighbours



def weaviate_generative_search(client, query: str,prompt: str, limit: int = 1, collection: str = "Article"):
    try:
        reviews = client.collections.get(collection)
        response = reviews.generate.near_text(
            query=query,
            single_prompt=prompt,
            limit=limit
        )

        return response
    finally:
        client.close()



class Client:
#  A wrapper class for intereating with all the tools generated in here
    def __init__(self, URL = "http://localhost:8080", APIKEY = "admin", openai_apikey = ""):
        # self.client = weaviate.connect_to_local(
        #     headers={
        #     "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"]  # Replace with your inference API key
        #         })
        # Connect to a WCS instance
        self.client = weaviate.connect_to_wcs(
            cluster_url=URL,
            auth_credentials=weaviate.auth.AuthApiKey(APIKEY),
                headers={
        "X-OpenAI-Api-Key": openai_apikey  # Replace with your inference API key
    }
)



    def ingest_data(self, file_name: str):
        with open(file_name, "r") as f:
            data = f.read()
        article = TEI().parse(data,"")
        self.save_article(article)




    def save_article(self, article):
        # Build article
        article = article.build()
 
        # Split authors string into a list of authors
        authors_list = article.get("authors").split('; ')

        affiliations_list = article.get("affiliations").split(',')
    
    # Create a list of author entries for the database
        data_authors = [{"name": author.strip(), "affiliation": article.get("affiliations")} for author in authors_list]
        # data_text_sections = [
        # {"name": section[0], "text": section["text"]} for section in article['sections']
        # ]
        data_paper ={
            "title": article.get("title"),
            "PublicationDate": article.get("publication"),
            "affiliation":article.get("affiliations"),
        }
        author_collection = self.client.collections.get("Author")
        paper_collection = self.client.collections.get("Paper")
        text_sections_collection = self.client.collections.get("TextSectionTemporal")


        #  Before adding a new uuid indentifier we must firt check on the dataset
        #  to see if the uuid already exists. If it does we must update the data
        paper_response = paper_collection.query.bm25(query=data_paper["title"], query_properties=["title"])
        if paper_response.objects:
            if paper_response.objects[0]:
                paper_uuid = paper_response.objects[0].uuid
        else:
            paper_uuid = paper_collection.data.insert(data_paper)



        for author in data_authors:
            authors_response = author_collection.query.bm25(query=author['name'], query_properties=["name"])
            if authors_response.objects:
                if authors_response.objects[0]:
                    author_uuid = authors_response.objects[0].uuid
            else:
                author_uuid = author_collection.data.insert(author)
            author_collection.data.reference_add(author_uuid,"hasPaper", paper_uuid)
            paper_collection.data.reference_add(paper_uuid,"hasAuthor", author_uuid)
            

        #  put in a batch the text sections
            
        
        for data_row in article['sections']:
            print(data_row)
            uuid_text_section = uuid.uuid4()
            text_sections_collection.data.insert(
            uuid=uuid_text_section,
            properties=data_row,
            )
            print("author")
            print(author_uuid)
            print("paper")
            print(paper_uuid)
            print("yext_uuid")
            print(uuid_text_section)
            # text_sections_collection.data.reference_add(uuid_text_section,"hasAuthor", author_uuid)
            text_sections_collection.data.reference_add(uuid_text_section,"hasPaper", paper_uuid)
        



    def init_schemas(self):
        """
        A class for initializing the schemas. This schemas are for modeling the data
        of scientific papers.
        """

        # Check if the hugginface vectorizer is availble if not use OpenAI
        # Overall Local Tools will lave more priority than Paid ones

    
        self.client.collections.create(
            name = "Paper",
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                Property(name="title", data_type=DataType.TEXT,),
                Property(name="PublicationDate", data_type=DataType.DATE),
                Property(name="affiliation", data_type=DataType.TEXT),
                
            ]
        )
        self.client.collections.create(
            name = "Author",
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                Property(name="name", data_type=DataType.TEXT,
                          vectorize_property_name= True),

            ]
        )
        self.client.collections.create(
            name = "TextSectionTemporal" ,
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="text", data_type=DataType.TEXT),
            ],
        )
        self.client.collections.create(
            name = "TextSection" ,
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                Property(name="section_title", data_type=DataType.TEXT),
                Property(name="section_text", data_type=DataType.TEXT),
                Property(name="section_id", data_type=DataType.INT),
                Property(name="parent_section_title", data_type=DataType.TEXT),

            ]
        )
        
        self.client.collections.create(
            name = "Figure",
            vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
            properties=[
                Property(name="figure_caption", data_type=DataType.TEXT),
                Property(name="figure_image", data_type=DataType.INT_ARRAY),
                
            ]
            )
    
        # Set references
        papers = self.client.collections.get("Paper")
        papers.config.add_reference(
        wvc.config.ReferenceProperty(name="hasAuthor",target_collection="Author"))
        papers.config.add_reference(
        ReferenceProperty(name="hasSection", target_collection="TextSection"))
        papers.config.add_reference(
        ReferenceProperty(name="hasReferencedPaper", target_collection="Paper"))
        papers.config.add_reference(
        ReferenceProperty(name="LinkPrediction", target_collection="Paper"))
        
        authors = self.client.collections.get("Author")
        authors.config.add_reference(ReferenceProperty(name="hasPaper", target_collection="Paper"),)
        authors.config.add_reference(ReferenceProperty(name="LinkPrediction", target_collection="Author"),)


        sections = self.client.collections.get("TextSectionTemporal")
        sections.config.add_reference(ReferenceProperty(name="hasPaper", target_collection="Paper"),)
        sections.config.add_reference(ReferenceProperty(name="hasAuthor", target_collection="Author"))
        sections.config.add_reference(ReferenceProperty(name="LinkPrediction", target_collection="TextSectionTemporal"))


