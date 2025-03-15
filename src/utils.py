import openai
import os
from config import settings
import base64
import streamlit as st
from html_templates import get_audio_template

audio_path = settings.AUDIO_PATH

def save_audio(recorded_audio, file_name):
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    with open(audio_path+file_name, "wb") as f:
        f.write(recorded_audio)

def audio_to_text(file_name):
    with open(audio_path+file_name, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    
def text_to_audio(text):
    response = openai.audio.speech.create(model="tts-1", voice="onyx", input=text)
    return response.content

def play_audio(file_name):
    with open(audio_path+file_name, "rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    st.markdown(get_audio_template(base64_audio), unsafe_allow_html=True)