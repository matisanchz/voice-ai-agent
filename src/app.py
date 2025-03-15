import os
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
from utils import play_audio, save_audio, text_to_audio, audio_to_text
import openai
import base64

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

print("ENTRADA")

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def get_ai_response(input_text, chat_history):

    #response = llm_gpt([HumanMessage(content=input_text)])

    response = retrieval_chain(input_text, chat_history)

    print(response["answer"])

    return response["answer"]

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

    vectorStore = Chroma.from_documents(docs, embedding = embedding, persist_directory=settings.CHROMA_DB_PATH)

    return vectorStore

def load_db():
    embedding = OpenAIEmbeddings()

    vectorStore = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embedding)
    
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

    chain = create_chain(vectorStore)
    
    return chain.invoke({
        "input": input_text,
        "chat_history": chat_history
    })

def main(vectorStore):
    st.title("Atom Voice Agent")
    st.write("Hi! Click on the voice recorder to interact with me.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    recorded_audio = audio_recorder()

    # Check if recording is done and available
    if recorded_audio:
        openai.api_key = settings.OPENAI_API_KEY

        save_audio(recorded_audio, audio_question_file)

        transcribed_text = audio_to_text(audio_question_file)

        st.write(transcribed_text)

        st.session_state.chat_history.append(HumanMessage(content=transcribed_text))

        ai_response = get_ai_response(transcribed_text, st.session_state.chat_history)
        
        st.session_state.chat_history.append(AIMessage(content=ai_response))
        
        print(st.session_state.chat_history)

        audio_response = text_to_audio(ai_response)

        save_audio(audio_response, audio_response_file)

        play_audio(audio_response_file)

        st.write(ai_response)

if __name__ == "__main__":
    if not os.path.exists(settings.CHROMA_DB_PATH):
        os.makedirs(settings.CHROMA_DB_PATH)
        docs = get_documents_from_web('https://atomchat.io/acerca-de-nosotros/')
        vectorStore = create_db(docs)
        print("ChromaDB created")
    else:
        vectorStore = load_db()
        print("ChromaDB loaded")

    main(vectorStore)