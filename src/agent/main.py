import streamlit as st
import os
import subprocess

import pickle
from pathlib import Path
import streamlit_authenticator as stauth

from dotenv import load_dotenv

from functions import get_files_text
from functions import get_text_chunks
from functions import get_vectorstore
from functions import get_conversation_chain
from agent import handle_user_input

favicon_path = os.path.join("logo", "browser.png")
if os.path.exists(favicon_path):
    st.set_page_config(page_title="AI Agent CSM", page_icon=favicon_path)
st.header("")

# --- USER AUTHENTICATION PRELIMINARY ONLY FOR TEST
names = ["Ubaldo Cordoba", "Yamil Colon"]
usernames = ["ubaldom.cordoba@upr.edu","ycolon@nd.edu"]

# Load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "AI_CSM", "abcdef", cookie_expiry_days=1)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status: 

    def uploader():
        txt = "Upload your file"
        accept = ['pdf', 'docx']
        files = st.file_uploader(txt, type=accept, accept_multiple_files=True)
        return files

    def get_openai_apikey():
        key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        return key

    def get_selected_sessions(hist):
        sessions = [i for i in enumerate(hist) if st.checkbox(f"Session {i+1}")]
        return sessions

    def erase_chat_history():
        hist = st.session_state.chat_history
        sessions = get_selected_sessions(hist)
        chat_history = [session for i, session in enumerate(hist) if i not in sessions]
        return chat_history

    def history():
        for i, session in enumerate(st.session_state.chat_history):
            st.checkbox(f"Session {i+1}")
            erase_history = st.button("Erase Selected Sessions")
            if erase_history:
                st.session_state.chat_history = erase_chat_history()
        return

    def main():
        """
        Sets up the Streamlit app and handles user interactions.

        The app allows users to upload files, process them, run a LAMMPS simulation,
        and chat with an AI agent.
        """
        load_dotenv()
        st.image(os.path.join("logo", "logo.png"), width=150)
        style = "'text-align: left; font-size: small;'"
        text = "Computational Soft Matter Research AI Agent"
        st.markdown(f"<div style={style}>{text}</div>", unsafe_allow_html=True)

        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "processComplete" not in st.session_state:
            st.session_state.processComplete = None

        with st.sidebar:
            st.sidebar.markdown(f"### Welcome {name}", unsafe_allow_html=True)
            uploaded_files = uploader()
            openai_api_key = get_openai_apikey()
            process = st.button("Process")
            lammps_script = st.text_area(" LAMMPS input script ")
            run_simulation = st.button("Run Simulation")

            show_history = st.checkbox("Show Chat History")
            if show_history:
                history()

            erase_all_history = st.button("Erase All Chat History")
            if erase_all_history:
                st.session_state.chat_history = []

            authenticator.logout("Logout", "sidebar")

        if process:
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
            files_text = get_files_text(uploaded_files)
            text_chunks = get_text_chunks(files_text)
            vetorestore = get_vectorstore(text_chunks)
            st.session_state.conversation = get_conversation_chain(vetorestore,openai_api_key)

            st.session_state.processComplete = True

        if st.session_state.processComplete == True:
            user_question = st.text_input("Ask Question about your files.")
            if user_question:
                handle_user_input(user_question)

        if run_simulation:
            if not lammps_script:
                st.warning("Please paste your LAMMPS input script to run the simulation.")
                st.stop()

            with open("lammps_input.in", "w") as f:
                f.write(lammps_script)

            st.info("Running LAMMPS simulation...")
            cmd = ["lammps", "-in", "lammps_input.in"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                st.error(f"Error running LAMMPS simulation:\n{stderr.decode('utf-8')}")
            else:
                st.success("LAMMPS simulation completed successfully.")

    if __name__ == '__main__':
        main()
