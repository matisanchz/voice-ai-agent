import os
import time
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import StreamlitChatMessageHistory

from agent import get_chat_memory, process_chat
from chat_session import get_chat_sessions
from config import settings
from utils import play_audio, save_audio, text_to_audio, audio_to_text
from html_templates import css, get_bot_template, get_form_template, get_user_template
import openai

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

def main():

    st.title("Atom Voice Agent")

    submit_button = None

    if "form" not in st.session_state:

        with st.form(key="user_form"):
            name = st.text_input("Enter your name")
            company = st.text_input("Enter your company")
            forecasting = st.number_input("Estimated Forecasting (in dollars)", min_value=0.0, step=0.01)

            all_filled = name and company and forecasting > 0

            submit_button = st.form_submit_button(label="Submit")

    if submit_button and all_filled:
        st.session_state.name = name
        st.session_state.company = company
        st.session_state.forecasting = forecasting
        st.session_state.form = "submitted"

        # Show confirmation that values were saved
        st.write("Form Submitted Successfully!")
        st.write(f"Name: {st.session_state.name}")
        st.write(f"Company: {st.session_state.company}")
        st.write(f"Estimated Forecasting: {st.session_state.forecasting}")

        time.sleep(5)

        st.rerun()

    elif submit_button:
        st.write("You have to fill all inputs.")

    if "form" in st.session_state:

        st.sidebar.title("Chat Sessions")

        chat_sessions = get_chat_sessions()

        st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key")

        st.write(css, unsafe_allow_html=True)

        chat_container = st.container()
        
        chat_memory = get_chat_memory()
        
        input_container = st.container(border=True)

        with input_container:
            user_input = st.chat_input("Type your message here", key="user_input")
            recorded_audio = audio_recorder(text="Click to record", icon_size="2x")

        if chat_memory is not None:
            with chat_container:
                for message in chat_memory:
                    if isinstance(message, HumanMessage):
                        st.write(get_user_template(message.content, message.type), unsafe_allow_html=True)
                    else:
                        st.write(get_bot_template(message.content, message.type), unsafe_allow_html=True)

        if user_input:
            recorded_audio = None
        else:
            user_input = None

        if openai.api_key != None:
            openai.api_key = settings.OPENAI_API_KEY

        if recorded_audio:
            save_audio(recorded_audio, audio_question_file)
            user_input = audio_to_text(audio_question_file)

        if user_input:
            
            with chat_container:
                st.write(get_user_template(user_input, "human"), unsafe_allow_html=True)
            
            ai_response = process_chat(user_input)
            
            with chat_container:
                st.write(get_user_template(ai_response, "ai"), unsafe_allow_html=True)
            
            audio_response = text_to_audio(ai_response)

            save_audio(audio_response, audio_response_file)

            play_audio(audio_response_file)
    else:
        # Show form content before submission
        st.write("Please fill in the form to start the chat.")
    #save_chat_history()

if __name__ == "__main__":
    main()