import streamlit as st
from audio_recorder_streamlit import audio_recorder
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain.chains import create_retrieval_chain

from config import settings
import openai
import base64

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

def get_ai_response(input_text, chat_history):

    #response = llm_gpt([HumanMessage(content=input_text)])

    response = retrieval_chain(input_text, chat_history)

    print(response["answer"])

    return response["answer"]

def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
    response.stream_to_file(audio_path)

def play_ai_response(audio_file):
    with open(audio_file, "rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    audio_html=f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

def get_documents_from_web(url):
    loader = WebBaseLoader(url)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 100,
        chunk_overlap = 20
    )
    splitDocs = splitter.split_documents(docs)
    return splitDocs

def create_db(docs):
    embedding = OpenAIEmbeddings()
    vectorStore = Chroma.from_documents(docs, embedding = embedding)
    return vectorStore

def create_chain(vectorStore):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AtomChai voice assistant, capable to answer and guide leads. Answer the user's questions based on the context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}") 
    ])

    chain = create_stuff_documents_chain(
        llm=llm_gpt,
        prompt=prompt

    )

    #retrieve info
    # search_kwargs={"k":2} search for the 2 most relevant docs
    retriever = vectorStore.as_retriever(search_kwargs={"k":2})

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name = "chat_history"),
        ("human", "{input}"),
        ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm=llm_gpt,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )
    return retrieval_chain

def retrieval_chain(input_text, chat_history):
    docs = get_documents_from_web('https://atomchat.io/acerca-de-nosotros/')
    vectorStore = create_db(docs)
    chain = create_chain(vectorStore)
    
    return chain.invoke({
        "input": input_text,
        "chat_history": chat_history
    })

def main():
    st.title("Atom Voice Agent")
    st.write("Hi! Click on the voice recorder to interact with me.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    recorded_audio = audio_recorder()

    # Check if recording is done and available
    if recorded_audio:
        openai.api_key = settings.OPENAI_API_KEY
        audio_question_file = settings.AUDIO_PATH+"audio_question.mp3"

        with open(audio_question_file, "wb") as f:
            f.write(recorded_audio)

        transcribed_text = transcribe_audio(audio_question_file)
        st.write(transcribed_text)

        st.session_state.chat_history.append(HumanMessage(content=transcribed_text))

        ai_response = get_ai_response(transcribed_text, st.session_state.chat_history)
        
        st.session_state.chat_history.append(AIMessage(content=ai_response))
        
        print(st.session_state.chat_history)

        response_audio_file = settings.AUDIO_PATH+"audio_response.mp3"
        text_to_audio(openai, ai_response, response_audio_file)
        play_ai_response(response_audio_file)
        st.write(ai_response)

if __name__ == "__main__":
    main()