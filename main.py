import os
import json
import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import tempfile

# Constants
MAX_DOCUMENT_TEXT_LENGTH = 5000  # Limit the document text to 5000 characters

# UI Design
st.set_page_config(
    page_title="MIDP_Chat",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for background color and styling
st.markdown(
    """
    <style>
        body {
            background-color: #f0f2f6;
        }
        .stApp {
            background-color: #e0e5ec;
        }
        .title {
            text-align: center;
            color: #4b4e6d;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Working directory and configuration
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

# API Key
GROQ_API_KEY = config_data["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize Groq client
client = Groq()

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Document text storage
if "document_text" not in st.session_state:
    st.session_state.document_text = ""


# Title
st.title("🦙 Welcome to MIDP_Chat")

# Sidebar for file uploading
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")

        # Limit the size of the extracted text
        st.session_state.document_text = text[:MAX_DOCUMENT_TEXT_LENGTH]
        st.success("Document uploaded and processed successfully!")

# Display message history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_prompt = st.chat_input("Ask MIDP...")
if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Construct the conversation messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *st.session_state.chat_history
    ]

    # Include limited document text as context
    if st.session_state.document_text:
        document_context = {
            "role": "system",
            "content": f"Reference Document (truncated): {st.session_state.document_text}"
        }
        messages.insert(1, document_context)

    # Get response from Groq API
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        assistant_response = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Display the assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    except Exception as e:
        st.error(f"Error: {str(e)}")