# AI-Agent-CSM-UPRM-UND
AI Agent CSM is a Streamlit web application that allows users to upload files, process them, run a LAMMPS simulation, and chat with an AI agent. The AI agent is powered by the OpenAI API and uses a conversational retrieval chain to interact with users. This version is to be hosted in servers and employ a vectorial database.

# Features
- Upload files: Users can upload PDF and DOCX files.
- Process files: Uploaded files are processed to extract text content.
- Run LAMMPS simulation: Users can paste their LAMMPS input script and run a simulation.
- Chat with AI agent: Users can ask questions and have a conversation with the AI agent.

# Usage:
To run the AI Agent CSM application, follow these steps:

# Install the required Python packages:

pip install -r requirements.txt

# Set the OpenAI API key:
python api.py

# Start the Streamlit application:

streamlit run main.py
Access the application in your web browser at http://localhost:8501.

# API
The RESTful API is used to set and retrieve the OpenAI API key. The API endpoints are:
- POST /api/set_api_key: Set the OpenAI API key.
- GET /api/get_api_key: Retrieve the OpenAI API key.

# Technologies Used
Python
Streamlit
OpenAI API
Flask (for the RESTful API)
PyPDF2, docx (for file processing)

# Future Work
- Integration with a vector database to store and enrich documents for the AI agent.
- Implementation of the RAG (Retrieval-Augmented Generation) methodology for better responses.
  
