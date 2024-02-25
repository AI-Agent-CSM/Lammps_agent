import weaviate
from weaviate.classes.config import Property, DataType, ReferenceProperty
import weaviate.classes as wvc
import argparse
import os
#  this is a file for ingesting XML Scientific data into Weaviate
# By using a tools like Grobib for converting pdfs to XML/TEI format
# to search in a smart way scientific papers.


# Initialize the Weaviate client

def main():

    client = weaviate.connect_to_local(
    cluster_url=os.getenv("WEAVIATE_URL"),
    headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"]  # Replace with your inference API key
    })






class Parser():
    # LIB/Text parser.

    def parse_xml(self, xml_file):
        # Parse the XML file using an XML parser like ElementTree.

        import xml.etree.ElementTree as ET

        tree = ET.parse(xml_file)
        root = tree.getroot()



    def get_batch_data(self, root):
        # Extract data from XML and return a list of dicts
        data = []

        for child in root:
            paper = {}
            paper["title"] = child.find("title").text
            paper["PublicationDate"] = child.find("date").text
            data.append(paper)

        return data
    
    def insert_pdf():
        # Uses Grobib for transforming the document to XML/TEI format
        pass





class Client:
#  A wrapper class for intereating with all the tools generated in here

    def __init__(self, client):
        self._parser = Parser()
        pass


    def start_services(self):
        pass


    def init_schemas(self,client, vectorizer :str, generative :str):
        """
        A class for initializing the schemas. This schemas are for modeling the data
        of scientific papers.
        """

        # Check if the hugginface vectorizer is availble if not use OpenAI
        # Overall Local Tools will lave more priority than Paid ones

        try:
            client.collections.create(
                name = "Paper",
                vectorizer_config = wvc.config.Configure.Vectorizer.text2vec_openai(),
                generative_config=wvc.config.Configure.Generative.cohere(),
                properties=[
                    Property(name="title", data_type=DataType.TEXT,),
                    Property("PublicationDate", data_type=DataType.DATE),
                    
                ],
                references=[
                    ReferenceProperty(name="hasAuthor", target_collection="Author"),
                    ReferenceProperty(name="hasSection", target_collection="TextSection"),

                ]
            )



            client.collections.create(
                "Author",
                properties=[
                    Property(name="author", data_type=DataType.TEXT),
                    Property(name="affiliation", data_type=DataType.TEXT),

                ],
                referencess=[
                    ReferenceProperty(name="hasPaper", target_collection="Paper"),
                ]
            )
            client.collections.create(
                "TextSection" ,
                properties=[
                    Property(name="section_title", data_type=DataType.TEXT),
                    Property(name="section_body", data_type=DataType.TEXT),
                    Property("chunk_id", data_type=DataType.INT),
                    Property("parent_section", data_type=DataType.TEXT),

                ],
                    
                    references = [
                        ReferenceProperty(name="hasPaper", target_collection="Paper"),

                    ]  )
            client.collections.create(
                "References")
            
            client.collections.create(
                name = "Figure",
                properties=[
                    Property(name="figure_caption", data_type=DataType.TEXT),
                    Property(name="figure_image", data_type=DataType.IMAGE),
                    
                ],
                references = [
                    ReferenceProperty(name="belongsToPaper", target_collection="Paper"),
                    ReferenceProperty(name="belongsToSection", target_collection="TextSection"),
                ]
                )
            
            client.collections.create(
                "Formula"
            )

            
        except:
            raise(Exception("Error creating the schemes. Probably becuase they already exist."))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()



  