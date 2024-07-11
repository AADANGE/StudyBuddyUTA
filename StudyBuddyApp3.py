import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

load_dotenv()

client = openai.OpenAI()
model = "gpt-3.5-turbo"
#"gpt-4-1106-preview"  
#"gpt-3.5-turbo"
#"gpt-4o"

# # Read the instruction file
# with open('instructions1.txt', 'r') as file:
#     instructions_data = file.read()

#read instruction file from streamlit secrets
instructions_streamlit = st.secrets["INSTRUCTIONS"]

#  == Hardcoded ids to be used once the first code run is done and the assistant was created
assis_id = "asst_f7hq4tAHr4cctjWjJZFkmoUx" 
thread_id = "thread_rUsXd9BZh31IfVI5p0BxLasP"

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Study Buddy", page_icon=":books:")
#st.set_page_config(page_title="Study Buddy", page_icon=":books:")


if st.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("Study Buddy")
st.write("How can I help you with your physics homework?")
st.write("Ask me things like:")
st.write(":blue[**Explain Quiz 4 question 3**] OR :blue[**Help solve module 3 question 1**] OR :blue[**What is time dilation?**]")

if st.button("Clear Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assis_id,
            instructions=instructions_streamlit
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")
        


