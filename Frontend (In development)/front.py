import streamlit as st
import requests
from PIL import Image
import base64
import io

def image_to_base64(image):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format='PNG')
    img_byte_array = img_byte_array.getvalue()
    return base64.b64encode(img_byte_array).decode('utf-8')

# Set page title and favicon
st.set_page_config(page_title='Login', page_icon=':lock:')

# Load logo image
logo_image = Image.open('uprm.png')

# Center the image
st.markdown(
    f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_to_base64(logo_image)}" style="width: 200px;"></div>',
    unsafe_allow_html=True
)

# Add text below the image
st.markdown("<h1 style='text-align: center;'>CSM UPRM</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>AI Agent for Soft Matter Research</h3>", unsafe_allow_html=True)

# Title
st.title('Login')

# Username and password inputs
username = st.text_input('Username')
password = st.text_input('Password', type='password')

# Login button
if st.button('Login'):
    # Prepare data to send to API
    data = {'username': username, 'password': password}

    # Make request to API
    response = requests.post('http://localhost:5000/login', json=data)

    # Process response
    if response.status_code == 200:
        st.success('Login successful')
        st.redirect('/path/to/main.py')  # Redirect to main.py (dashboard)
    else:
        st.error('Invalid username or password')

# Sign-up section
st.markdown('---')  # I did this is to add a horizontal line to separate the sections
st.title('Sign Up')
new_username = st.text_input('New Username')
new_password = st.text_input('New Password', type='password')
email = st.text_input('Email')  # Add an email input field
# Add more input fields for other user information (e.g., institution)

if st.button('Sign Up'):
    # Prepare data to send to API
    data = {'username': new_username, 'password': new_password, 'email': email}
    # Add more fields to the data dictionary for other user information

    # Make request to API
    response = requests.post('http://localhost:5000/signup', json=data)

    # Process response
    if response.status_code == 201:
        st.success('Sign up successful')
        # Redirect to login page or do other actions
    else:
        st.error('Sign up failed. Username may already exist or other error occurred.')

