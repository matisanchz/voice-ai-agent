
import os
from dotenv import load_dotenv
from config import settings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_message_histories.upstash_redis import UpstashRedisChatMessageHistory

from utils import get_timestamp

load_dotenv()

class ChromaDataBase():

    def get_vectorstore(self):
        if not os.path.exists(settings.CHROMA_DB_PATH):
            os.makedirs(settings.CHROMA_DB_PATH)
            docs = self.get_documents_from_web(os.getenv("ATOM_URL"))
            print("ChromaDB created")
            return self.create_db(docs)
        else:
            print("ChromaDB loaded")
            return self.load_db()

    def get_documents_from_web(self, url):
        loader = WebBaseLoader(url)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 100,
            chunk_overlap = 20
        )
        splitDocs = splitter.split_documents(docs)
        return splitDocs

    def create_db(self, docs):
        embedding = OpenAIEmbeddings()
        vectorStore = Chroma.from_documents(docs, embedding = embedding, persist_directory=settings.CHROMA_DB_PATH)

        return vectorStore

    def load_db(self):
        embedding = OpenAIEmbeddings()
        vectorStore = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embedding)
        
        return vectorStore

    def get_retriever(self):
        vectorStore = self.get_vectorstore()
        return vectorStore.as_retriever(search_kwargs={"k":2})
    
class RedisDataBase():

    def __init__(self):
         self.history = UpstashRedisChatMessageHistory(
                url=os.getenv("UPSTASH_REDIS_REST_URL"),
                token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
                session_id = "sessions",
                ttl=0
            )

    def create_session(self):

        session_id = self.get_last_session_id()

        timestamp = get_timestamp()

        session_name = timestamp+settings.SESSION_ID_KEY_TEMPLATE+str(session_id)

        self.save_session(session_name)

        return session_name

    def get_last_session_id(self):

        last_session_id = self.history.redis_client.get("last_session_id")

        if last_session_id:
            new_session_id = int(last_session_id) + 1
        else:
            new_session_id = 1

        self.history.redis_client.set("last_session_id", new_session_id)

        return new_session_id
    
    def save_session(self, session_name):
        self.history.redis_client.rpush("list_sessions", session_name)

    def get_sessions(self):
        sessions = self.history.redis_client.lrange("list_sessions", 0, -1)
        return sessions[::-1]
