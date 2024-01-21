from fastapi import FastAPI, File, UploadFile
import subprocess
import os

app = FastAPI()

@app.post("/run-lammps/")
async def run_lammps(file: UploadFile = File(...)):
    with open("input_file.in", "wb") as buffer:
        buffer.write(await file.read())

    # Running LAMMPS simulation
    process = subprocess.run(["lmp_mpi", "-in", "input_file.in"], capture_output=True, text=True)

    # Return the output
    return {"output": process.stdout, "error": process.stderr}

