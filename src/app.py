import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from config import settings
from langchain.schema import HumanMessage, SystemMessage, AIMessage

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def main():
    st.title("Atom Voice Agent")
    st.write("Hi! Click on the voice recorder to interact with me.")

    recorded_audio = audio_recorder()
    
    # Check if recording is done and available
    if recorded_audio:
        audio_file = settings.AUDIO_PATH+"audio_question.mp3"
        with open(audio_file, "wb") as f:
            f.write(recorded_audio)

if __name__ == "__main__":
    main()