
from src.laamps_types import LammpsOptions
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
import os
import tempfile
import aiofiles
from typing import List
from  src.weaviate_search.weaviate_database import Client
from src.weaviate_search.context_search import WeaviateContextSearch
import subprocess
from src.api.grobid_client_python.grobid_client.grobid_client import GrobidClient
app = FastAPI()


@app.post("/run-lammps/")
async def run_lammps(file: UploadFile = File(...)):
    # Write the uploaded file to disk
    input_filename = "input_file.in"
    with open(input_filename, "wb") as buffer:
        buffer.write(await file.read())

    # Construct the LAMMPS command line to run the input file
    cmd = ["lmp", "-in", input_filename]

    # Execute the LAMMPS command
    process = subprocess.run(cmd, capture_output=True, text=True)

    # Return the output
    if process.returncode == 0:
        return {"output": process.stdout}
    else:
        raise HTTPException(status_code=400, detail=process.stderr)

@app.post("/run-lammps-streaming/")
async def run_lammps_streaming(file: UploadFile = File(...)):
    with open("input_file_stream.in", "wb") as buffer:
        buffer.write(await file.read())

    def generate_output():
        # Here, we use subprocess.Popen to start the simulation and stream its output
        process = subprocess.Popen(["lmp", "-in", "input_file_stream.in"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Stream stdout line by line
        for line in process.stdout:
            yield line

        # Ensure the subprocess finishes and include stderr at the end if there's any error
        process.wait()
        if process.returncode != 0:
            yield process.stderr.read()

    return StreamingResponse(generate_output(), media_type="text/plain")





class SearchSchema(BaseModel):
    query: str
    reference: str
    limit: int
    collection: str
    properties: List[str]
    references_properties: List[str]
@app.post("/feature-search/")
async def context_search(search_schema: SearchSchema):
    c = Client()
    search = WeaviateContextSearch(c.client)
    search_results = search.context_search(
        search_schema.query, 
        search_schema.reference, 
        search_schema.limit, 
        search_schema.collection, 
        search_schema.properties, 
        search_schema.references_properties
    )
    return search_results

@app.post("/feature-search-streaming/")
async def add_file_paper(file: UploadFile = File(...)):
    # Create a temporary directory

   
    async with aiofiles.open("/home/cesar/Projects/Lammps_agent/test/temp.pdf", 'wb') as temp_file:
        content = await file.read()
        await temp_file.write(content)

        # Initialize your client with its config
        client = GrobidClient(config_path="/home/cesar/Projects/Lammps_agent/test/grobib_config.json")

        # Process the directory
        output_file = "tmp_file.tei"
        client.process(service="processFulltextDocument", input_path="/home/cesar/Projects/Lammps_agent/test", n=20)

        c = Client()
        c.ingest_data("/home/cesar/Projects/Lammps_agent/test/temp.grobid.tei.xml")
    return {"filename": file.filename, "processed": True}



# Example of Request

