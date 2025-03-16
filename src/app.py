import os
import time
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from streamlit_carousel import carousel

from agent import AgentManager

from config import settings
from database import RedisDataBase
from utils import play_audio, save_audio, text_to_audio, audio_to_text
from html_templates import css, get_bot_template, get_user_template
import openai

from validator import validate_name

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

def main():

    st.title("Atom Voice Agent")

    submit_button = None

    if "session_key" not in st.session_state:

        with st.container(border=True, key="avatar_container"):

            images = {
                f"Avatar {i}": {
                    "id": 219953 + i,  # Unique ID
                    "url": settings.FLATICON_REPO + f"{219953 + i}.png"
                }
                for i in range(1, 25)
            }

            avatar_choice = st.selectbox("Select an image:", list(images.keys()))

            st.image(images[avatar_choice]["url"], caption=avatar_choice, width=100)

            model = None

            with st.form(key="user_form"):
                name = st.text_input("Enter your name")
                company = st.text_input("Enter your company")
                country = st.text_input("Enter your country")
                forecasting = st.number_input("Estimated Forecasting (in dollars)", min_value=10, step=10)

                all_filled = name and company and forecasting > 0

                submit_button = st.form_submit_button(label="Submit")
    else:
        if "avatar" in st.session_state:
            if "session_selected" in st.session_state:
                model = AgentManager(st.session_state.session_selected)
                st.session_state.model = model
            else:
                model = st.session_state.model

    if submit_button:
        if all_filled:
            if name:
                if validate_name(name) == "1":
                    st.session_state.name = name
                    st.session_state.company = company
                    st.session_state.country = country
                    st.session_state.forecasting = forecasting
                    st.session_state.form = "submitted"
                    st.session_state.avatar_id = images[avatar_choice]["id"]

                    # Show confirmation that values were saved
                    st.write("Form Submitted Successfully!")
                    st.write(f"Name: {st.session_state.name}")
                    st.write(f"Company: {st.session_state.company}")
                    st.write(f"Estimated Forecasting: {st.session_state.forecasting}")
                    
                    chatSessionManager = RedisDataBase()

                    session_key = chatSessionManager.create_session()

                    st.session_state.session_key = session_key

                    model = AgentManager(session_key)

                    st.session_state.model = model

                    time.sleep(3)

                    st.rerun()
                else:
                    st.write("You must use a real name. It is forbidden to use numbers or special characters.")
        else:
            st.write("You have to fill all inputs.")

    if "session_key" in st.session_state:

        st.sidebar.title("Chat Sessions")

        redis_db = RedisDataBase()

        chat_sessions = redis_db.get_sessions()

        st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_selected")

        st.write(css, unsafe_allow_html=True)

        chat_container = st.container()

        chat_memory = model.get_chat_memory()
        
        input_container = st.container(border=True)

        with input_container:
            user_input = st.chat_input("Type your message here", key="user_input")
            recorded_audio = audio_recorder(text="Click to record", icon_size="2x")

        if chat_memory is not None:
            with chat_container:
                for message in chat_memory:
                    if isinstance(message, HumanMessage):
                        st.write(get_user_template(message.content, message.type, st.session_state.avatar_id), unsafe_allow_html=True)
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
                st.write(get_user_template(user_input, "human", st.session_state.avatar_id), unsafe_allow_html=True)
            
            ai_response = model.process_chat(user_input)
            
            with chat_container:
                st.write(get_bot_template(ai_response, "ai"), unsafe_allow_html=True)
            
            audio_response = text_to_audio(ai_response)

            save_audio(audio_response, audio_response_file)

            play_audio(audio_response_file)
    else:
        st.write("Please fill in the form to start the chat.")

if __name__ == "__main__":
    main()