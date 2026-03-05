#!/usr/bin/env python3
"""
Streamlit Chatbot Application

This script creates a simple chatbot web application using Streamlit and OpenAI.
The chatbot acts as a polite academic teacher answering questions in hip-hop style.

Required environment variables:
- OPENAI_API_KEY: Your OpenAI API key

To run the application:
1. Install dependencies: pip install streamlit openai python-dotenv
2. Set your OPENAI_API_KEY in .env file
3. Run: streamlit run 4_Your_own_chatbot.py
4. Open browser to the displayed URL (usually http://localhost:8501)

For public access (optional):
1. Install localtunnel: npm install -g localtunnel
2. Run the app: streamlit run 5. Your\ own\ chatbot.py
3. In another terminal: npx localtunnel --port 8501
4. Use the generated URL for public access
"""

from dotenv import load_dotenv
import os
from openai import OpenAI
import streamlit as st

# Load environment variables from .env file
load_dotenv(override=True)

def initialize_client():
    """Initialize OpenAI client with API key from environment"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("OPENAI_API_KEY environment variable is required")
        st.stop()
    
    return OpenAI(api_key=api_key)

"""Main Streamlit application"""

# Page configuration
st.set_page_config(
    page_title="My Own Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 My Own Chatbot!")
st.caption("A polite academic teacher answering questions in hip-hop style")

# Initialize OpenAI client
client = initialize_client()

# Initialize session state variables
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "You are a polite academic teacher answering students' questions in a hip-hop style"
        }
    ]

# Model selection in sidebar
with st.sidebar:
    st.header("Settings")
    model_option = st.selectbox(
        "Choose Model:",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0
    )
    st.session_state["openai_model"] = model_option
    
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {
                "role": "system", 
                "content": "You are a polite academic teacher answering students' questions in a hip-hop style"
            }
        ]
        st.rerun()
    
    st.info("💡 **Tip**: This chatbot combines academic knowledge with hip-hop flair!")

# Display chat messages (excluding system message)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Hi, what's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        try:
            # Create streaming response
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Stream the response
            response = st.write_stream(stream)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.info("Please check your API key and try again.")
