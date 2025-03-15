import os
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from agent import process_chat
from config import settings
from utils import play_audio, save_audio, text_to_audio, audio_to_text
from html_templates import css, get_bot_template, get_user_template
import openai

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

model = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def main():

    st.title("Atom Voice Agent")

    st.write(css, unsafe_allow_html=True)

    chat_container = st.container()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    input_container = st.container(border=True)

    with input_container:
        user_input = st.chat_input("Type your message here", key="user_input")
        recorded_audio = audio_recorder(text="Click to record", icon_size="2x")

    with chat_container:
        for message in st.session_state.chat_history:
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

        st.session_state.chat_history.append(HumanMessage(content=user_input))

        ai_response = process_chat(user_input, st.session_state.chat_history)

        with chat_container:
            st.write(get_user_template(ai_response, "ai"), unsafe_allow_html=True)

        st.session_state.chat_history.append(AIMessage(content=ai_response))

        audio_response = text_to_audio(ai_response)

        save_audio(audio_response, audio_response_file)

        play_audio(audio_response_file)

if __name__ == "__main__":
    main()