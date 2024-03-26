import streamlit as st
import os
import subprocess
from dotenv import load_dotenv
import requests

def verify_username(username):
    response = requests.post('http://localhost:8000/verify_username', json={'username': username})
    if response.status_code == 200:
        return True
    else:
        return False

def get_session_history_file(username):
    session_history_file = f"{username}_session_history.txt"
    if os.path.exists(session_history_file):
        return session_history_file
    else:
        return None

def main():
    load_dotenv()
    favicon_path = os.path.join("logo", "browser.png")
    if os.path.exists(favicon_path):
        st.set_page_config(page_title="AI Agent CSM", page_icon=favicon_path)
    st.header("")
    st.image(os.path.join("logo", "logo.png"), width=100)
    st.markdown("<div style='text-align: left; font-size: small;'>Computational Soft Matter Research AI Agent</div>", unsafe_allow_html=True)

    username = st.text_input("Enter your username")

    if st.button("Verify"):
        if verify_username(username):
            st.session_state["username"] = username
            st.success("Username verified")
        else:
            st.error("Username verification failed")

    username = st.session_state.get("username")

    session_history_file = get_session_history_file(username)

    if session_history_file:
        with open(session_history_file, "r") as f:
            st.session_state.chat_history = f.readlines()

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None

    with st.sidebar:
        uploaded_files = st.file_uploader("Upload your file", type=['pdf', 'docx'], accept_multiple_files=True)
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        process = st.button("Process")
        lammps_script = st.text_area(" LAMMPS input script ")
        run_simulation = st.button("Run Simulation")
        show_history = st.checkbox("Show Chat History")
        if show_history:
            for i, session in enumerate(st.session_state.chat_history):
                st.checkbox(f"Session {i+1}")
            erase_history = st.button("Erase Selected Sessions")
            if erase_history:
                selected_sessions = [i for i, selected in enumerate(st.session_state.chat_history) if
                                      st.checkbox(f"Session {i+1}")]
                st.session_state.chat_history = [session for i, session in enumerate(st.session_state.chat_history) if
                                                 i not in selected_sessions]

        erase_all_history = st.button("Erase All Chat History")
        if erase_all_history:
            st.session_state.chat_history = []

    if process:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        files_text = get_files_text(uploaded_files)
        text_chunks = get_text_chunks(files_text)
        vetorestore = get_vectorstore(text_chunks)
        st.session_state.conversation = get_conversation_chain(vetorestore, openai_api_key)
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
        process = subprocess.Popen(["lammps", "-in", "lammps_input.in"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            st.error(f"Error running LAMMPS simulation:\n{stderr.decode('utf-8')}")
        else:
            st.success("LAMMPS simulation completed successfully.")

if __name__ == '__main__':
    main()
