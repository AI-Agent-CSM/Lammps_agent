import openai
import subprocess
import streamlit as s

def handle_user_input(user_question):
    """
    Handles user input and generates a response from the chatbot.

    Args:
        user_question (str): User's question.

    Returns:
        None
    """
    if "generate LAMMPS script" in user_question.lower() or "generate lammps script" in user_question.lower():
        prompt = """
        Generate a LAMMPS input script for a simulation based on the request description.
        
        User Input: {user_input}

        {missing_data_prompt} 
        """

        # I added this to request a completion from the OpenAI API
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            stop=None
        )

        # For extracting the generated LAMMPS script from the response
        lammps_script = response.choices[0].text.strip()

        # This is to update the Streamlit app's state to set the LAMMPS script in the text area
        st.session_state.lammps_script = lammps_script

        # To display a message to the user indicating that the LAMMPS script has been generated
        st.info("LAMMPS script generated. You can now run the simulation.")

    elif "run LAMMPS simulation" in user_question.lower() or "run lammps simulation" in user_question.lower():
        if "lammps_script" in st.session_state:
            # Saves the LAMMPS input script to a file
            with open("lammps_input.in", "w") as f:
                f.write(st.session_state.lammps_script)

            # Runs the LAMMPS simulation
            st.info("Running LAMMPS simulation...")
            process = subprocess.Popen(["lammps", "-in", "lammps_input.in"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                st.error(f"Error running LAMMPS simulation:\n{stderr.decode('utf-8')}")
            else:
                st.success("LAMMPS simulation completed successfully.")
        else:
            st.warning("No LAMMPS script generated yet. Please generate the script before running the simulation.")

    else:
        # For handling other inputs here if needed in the future
        pass

    with get_openai_callback() as cb:
        response = st.session_state.conversation({'question': user_question})
        chat_history = st.session_state.chat_history or []
        chat_history.append(response)
        st.session_state.chat_history = chat_history

    # Layout of input/response containers
    response_container = st.container()

    with response_container:
        for i, messages in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                message(messages.content, is_user=True, key=str(i))
            else:
                message(messages.content, key=str(i))
        st.write(f"Total Tokens: {cb.total_tokens}" f", Prompt Tokens: {cb.prompt_tokens}" f", Completion Tokens: {cb.completion_tokens}" f", Total Cost (USD): ${cb.total_cost}")
