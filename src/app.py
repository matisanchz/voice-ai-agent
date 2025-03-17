import time
import openai
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain.schema import HumanMessage

from agent import AgentManager
from config import settings
from database import RedisDataBase, SQLDataBase
from utils import get_countries, play_audio, save_audio, text_to_audio, audio_to_text
from html_templates import css, get_bot_template, get_user_template
from validator import validate_name

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

def clean_variable_sesion():
    """
    Clear all variables from the Streamlit session.

    Returns
    -------
    None
    """
    st.session_state.clear()

def main():

    """
    Entry point of the application.
    
    Returns
    -------
    None
    """

    st.title("Atom Voice Agent")

    st.write(css, unsafe_allow_html=True)

    redis_db = RedisDataBase()

    chat_sessions = redis_db.get_sessions()

    chat_sessions_with_placeholder = ["Select an option..."] + chat_sessions

    selected = None

    if chat_sessions and len(chat_sessions) > 0:
        st.sidebar.title("Chat Sessions")
        selected = st.sidebar.selectbox("Select a chat session", chat_sessions_with_placeholder, index=0, key="session_selected")
    
    if selected and selected != "Select an option...":
        if "session_key" not in st.session_state:
            st.session_state.session_key = selected
            print("Entro1")

    submit_button = None

    if "session_key" not in st.session_state:

        with st.container(border=True, key="avatar_container"):

            images = {
                f"Avatar {i}": {
                    "id": settings.FLATICON_REPO_NUM + i,
                    "url": settings.FLATICON_REPO + f"{settings.FLATICON_REPO_NUM + i}.png"
                }
                for i in range(1, 25)
            }

            col1, col2, col3 = st.columns([2, 1, 2])

            with col2:
                avatar_choice = st.selectbox("Select an Avatar:", list(images.keys()))
                st.image(images[avatar_choice]["url"], caption=avatar_choice, width=100)

            model = None

            with st.form(key="user_form"):
                name = st.text_input("Enter your name")
                company = st.text_input("Enter your company")
                country = st.selectbox("Select a Country:", get_countries())
                budget = st.number_input("Estimated Budget (in dollars)", min_value=100, step=100)

                all_filled = name and company and budget > 0

                submit_button = st.form_submit_button(label="Submit")
    else:
        print("Entro2")
        if "session_selected" in st.session_state and st.session_state.session_selected != "Select an option..." and (st.session_state.session_selected != st.session_state.session_key):
                print("Entro3")
                user = SQLDataBase().get_user_by_id((st.session_state.session_selected.split('_'))[-1])
                st.session_state.name, st.session_state.avatar_id, st.session_state.company, st.session_state.country, st.session_state.budget = user
                model = AgentManager(st.session_state.session_selected, user, False)
                st.session_state.model = model
                st.session_state.session_key = st.session_state.session_selected
                st.rerun()
        else:
            if "model" in st.session_state:
                model = st.session_state.model
            else:
                user = SQLDataBase().get_user_by_id((st.session_state.session_key.split('_'))[-1])
                st.session_state.name, st.session_state.avatar_id, st.session_state.company, st.session_state.country, st.session_state.budget = user
                model = AgentManager(st.session_state.session_selected, user, False)
                st.session_state.model = model
                st.rerun()

    if submit_button:
        if all_filled:
            if name:
                if validate_name(name) == "1":
                    st.session_state.name = name
                    st.session_state.avatar_id = images[avatar_choice]["id"]
                    st.session_state.company = company
                    st.session_state.country = country
                    st.session_state.budget = budget
                    st.session_state.form = "submitted"

                    user = [name, images[avatar_choice]["id"], company, country, budget]

                    st.write("Form Submitted Successfully!")
                    st.write(f"Name: {st.session_state.name}")
                    st.write(f"Company: {st.session_state.company}")
                    st.write(f"Estimated Budget: {st.session_state.budget}")

                    redis_db = RedisDataBase()

                    session_key = redis_db.create_session()

                    session_num = (session_key.split('_'))[-1]

                    st.session_state.session_key = session_key

                    sql_db = SQLDataBase()

                    sql_db.insert_user(session_num, st.session_state.name, st.session_state.avatar_id, st.session_state.company,
                        st.session_state.country, st.session_state.budget)

                    model = AgentManager(session_key, user, True)

                    st.session_state.model = model

                    time.sleep(3)

                    st.rerun()
                else:
                    st.write("You must use a real name. It is forbidden to use numbers or special characters.")
        else:
            st.write("You have to fill all inputs.")

    if "session_key" in st.session_state:
        st.write(css, unsafe_allow_html=True)

        chat_container = st.container()

        if model.first_msg:
            with chat_container:
                model.get_first_msg()

        chat_memory = model.get_chat_memory()
        
        input_container = st.container(border=True)

        with input_container:
            user_input = st.chat_input("Type your message here", key="user_input")
            recorded_audio = audio_recorder(text="Click to record", icon_size="2x")

        if chat_memory is not None:
            with chat_container:
                for message in chat_memory:
                    if isinstance(message, HumanMessage):
                        st.write(get_user_template(message.content, st.session_state.avatar_id), unsafe_allow_html=True)
                    else:
                        st.write(get_bot_template(message.content), unsafe_allow_html=True)

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
                st.write(get_user_template(user_input, st.session_state.avatar_id), unsafe_allow_html=True)
            
            ai_response = model.process_chat(user_input)
            
            with chat_container:
                st.write(get_bot_template(ai_response), unsafe_allow_html=True)
            
            audio_response = text_to_audio(ai_response)

            save_audio(audio_response, audio_response_file)

            play_audio(audio_response_file)
        
        with st.container(key="buttons"):
            col1, col2 = st.columns(2)
            with col1:
                delete = st.button("Delete Chat")
            with col2:
                new = st.button("New session")
        if delete:
            session_key = st.session_state.session_key
            sql_db = SQLDataBase()
            redis_db = RedisDataBase()
            clean_variable_sesion()
            sql_db.delete_user((session_key.split('_'))[-1])
            redis_db.delete_session(session_key)
            redis_db.delete_chat(session_key)
            time.sleep(4)
            st.rerun()
        if new:
            clean_variable_sesion()
            time.sleep(3)
            st.rerun()
    else:
        st.write("Please fill in the form to start the chat.")

if __name__ == "__main__":
    main()