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
from html_templates import css, get_bot_template, get_user_template
import openai
import base64

audio_question_file = "audio_question.mp3"
audio_response_file = "audio_response.mp3"

llm_gpt = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

def get_ai_response(input_text, chat_history):

    #response = llm_gpt([HumanMessage(content=input_text)])

    response = retrieval_chain(input_text, chat_history)

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

    if recorded_audio:
        if openai.api_key != None:
            openai.api_key = settings.OPENAI_API_KEY

        save_audio(recorded_audio, audio_question_file)

        user_input = audio_to_text(audio_question_file)


    if user_input:

        with chat_container:
            st.write(get_user_template(user_input, "human"), unsafe_allow_html=True)

        st.session_state.chat_history.append(HumanMessage(content=user_input))

        ai_response = get_ai_response(user_input, st.session_state.chat_history)

        with chat_container:
            st.write(get_user_template(ai_response, "ai"), unsafe_allow_html=True)

        st.session_state.chat_history.append(AIMessage(content=ai_response))

        audio_response = text_to_audio(ai_response)

        save_audio(audio_response, audio_response_file)

        play_audio(audio_response_file)

if __name__ == "__main__":
    if not os.path.exists(settings.CHROMA_DB_PATH):
        os.makedirs(settings.CHROMA_DB_PATH)
        docs = get_documents_from_web('https://atomchat.io/acerca-de-nosotros/')
        vectorStore = create_db(docs)
        print("ChromaDB created")
    else:
        vectorStore = load_db()
        print("ChromaDB loaded")

    main()