
from src.laamps_types import LammpsOptions
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import subprocess
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