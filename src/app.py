import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from config import settings
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import openai
import base64

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

def get_ai_response(input_text):
    response = llm_gpt([HumanMessage(content=input_text)])
    return response.content

def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
    response.stream_to_file(audio_path)

def play_ai_response(audio_file):
    with open(audio_file, "rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    audio_html=f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

def main():
    st.title("Atom Voice Agent")
    st.write("Hi! Click on the voice recorder to interact with me.")

    recorded_audio = audio_recorder()
    
    # Check if recording is done and available
    if recorded_audio:
        openai.api_key = settings.OPENAI_API_KEY
        audio_question_file = settings.AUDIO_PATH+"audio_question.mp3"

        with open(audio_question_file, "wb") as f:
            f.write(recorded_audio)

        transcribed_text = transcribe_audio(audio_question_file)
        st.write(transcribed_text)

        ai_response = get_ai_response(transcribed_text)
        response_audio_file = settings.AUDIO_PATH+"audio_response.mp3"
        text_to_audio(openai, ai_response, response_audio_file)
        play_ai_response(response_audio_file)
        st.write(ai_response)

if __name__ == "__main__":
    main()