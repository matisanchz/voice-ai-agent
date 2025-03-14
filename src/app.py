import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from config import settings
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import openai

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

def main():
    st.title("Atom Voice Agent")
    st.write("Hi! Click on the voice recorder to interact with me.")

    recorded_audio = audio_recorder()
    
    # Check if recording is done and available
    if recorded_audio:
        openai.api_key = settings.OPENAI_API_KEY
        audio_file = settings.AUDIO_PATH+"audio_question.mp3"
        with open(audio_file, "wb") as f:
            f.write(recorded_audio)

        transcribed_text = transcribe_audio(audio_file)

        print(transcribed_text)

if __name__ == "__main__":
    main()