
from ..laamps_types import LammpsOptions
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
import os
import tempfile
import aiofiles
from typing import List
from  ..weaviate_search.weaviate_database import Client
from ..weaviate_search.context_search import WeaviateContextSearch
import subprocess
from tempfile import NamedTemporaryFile
from fastapi.responses import JSONResponse
from ..api.grobid_client_python.grobid_client.grobid_client import GrobidClient
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

@app.post("/add-file-paper/")
async def add_file_paper(file: UploadFile = File(...)):
    # Create a temporary file for the uploaded PDF
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        # Async write to temporary file
        async with aiofiles.open(temp_pdf.name, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Initialize the Grobid client with its configuration
        client = GrobidClient(config_path="config/grobib_config.json")
        if not os.path.exists("result"):
            os.mkdir("./result")


        output_path = "./result"
        client.process(service="processFulltextDocument", input_path=temp_pdf.name, output=output_path, n=1)
        # Assume Grobid writes output to a specific file within 'output_path'
        output_file = f"{output_path}/output.tei.xml"

        # Ingest data - Assuming 'Client' is previously defined and works as intended
        c = Client()
        c.ingest_data(output_file)

    return JSONResponse(content={"filename": file.filename, "processed": True})


# Example of Request

