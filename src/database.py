
import os
import sqlite3
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.chat_message_histories.upstash_redis import UpstashRedisChatMessageHistory
from langchain_community.utilities import SQLDatabase
from langchain.document_loaders import PyMuPDFLoader

from utils import get_all_pdf_files, get_all_urls, get_timestamp
from config import settings

load_dotenv()

"""
This class provides the chroma database connection, 
and functionalities.
"""
class ChromaDataBase():

    def get_vectorstore(self):
        """
        Get the Chroma vectorstore, to search for information.

        Returns
        -------
        Chroma
            The vectorstore.
        """
        if not os.path.exists(settings.CHROMA_DB_PATH):
            os.makedirs(settings.CHROMA_DB_PATH)
            web_docs = self.get_documents_from_web(get_all_urls())
            pdf_docs = self.get_documents_from_pdfs(get_all_pdf_files())
            all_docs = web_docs + pdf_docs
            print("ChromaDB created")
            return self.create_db(all_docs)
        else:
            print("ChromaDB loaded")
            return self.load_db()

    def get_documents_from_web(self, urls):
        """
        Get the documents from the list of urls.

        Parameters
        ----------
        urls : List[str]
            List of urls to scrap.

        Returns
        -------
        List[Document]
            The documents splitted by chunks.
        """
        all_docs = []

        for url in urls:
            loader = WebBaseLoader(url)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=100,
                chunk_overlap=20
            )

            splitDocs = splitter.split_documents(docs)
            
            all_docs.extend(splitDocs)
        
        return all_docs

    def get_documents_from_pdfs(self, pdf_paths):
        """
        Get the pdf information from the list of paths.

        Parameters
        ----------
        urls : List[str]
            List of path to scrap pdf documents.

        Returns
        -------
        List[Document]
            The documents splitted by chunks.
        """
        docs = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

        for path in pdf_paths:
            loader = PyMuPDFLoader(path)
            pdf_docs = loader.load()
            split_docs = splitter.split_documents(pdf_docs)
            docs.extend(split_docs)
        
        return docs

    def create_db(self, docs):
        """
        Creates the database on disk, if not exists, and fill with the documents.

        Parameters
        ----------
        urls : List[Document]
            List of Documents to persist.

        Returns
        -------
        List[]
            The documents splitted by chunks.
        """
        embedding = OpenAIEmbeddings()
        vectorStore = Chroma.from_documents(docs, embedding = embedding, persist_directory=settings.CHROMA_DB_PATH)

        return vectorStore

    def load_db(self):
        """
        Loads the database if exists.

        Returns
        -------
        None
        """
        embedding = OpenAIEmbeddings()
        vectorStore = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embedding)
        
        return vectorStore

    def get_retriever(self):
        """
        Gets the retriever capable to search for documents.

        Returns
        -------
        VectorStoreRetriever
            The retriever from ChromaDB.
        """
        vectorStore = self.get_vectorstore()
        return vectorStore.as_retriever(search_kwargs={"k":2})
    
"""
This class provides the redis database connection, 
and functionalities.
"""
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
    
    def delete_session(self, session_name):
        self.history.redis_client.lrem("list_sessions", 0, session_name)
    
    def save_session(self, session_name):
        self.history.redis_client.rpush("list_sessions", session_name)

    def get_sessions(self):
        sessions = self.history.redis_client.lrange("list_sessions", 0, -1)
        return sessions[::-1]
    
    def delete_chat(self, session_name):
        self.history.redis_client.delete("message_store:"+session_name)

"""
This class provides the sqlite database connection, 
and functionalities.
"""
class SQLDataBase():
    def __init__(self):
        self.conn = sqlite3.connect("chatbot_db.sqlite")
        self.db = SQLDatabase.from_uri("sqlite:///chatbot_db.sqlite")

        self.create_user_table()
    
    def create_user_table(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                name TEXT,
                avatar INT,
                company TEXT,
                country TEXT,
                budget INT
            )
        ''')

        self.conn.commit()

    def insert_user(self, id, name, avatar, company, country, budget):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO user (id, name, avatar, company, country, budget) VALUES (?, ?, ?, ?, ?, ?)", (id, name, avatar, company, country, budget))
        self.conn.commit()

    def delete_user(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = ?", (id,))
        self.conn.commit()

    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()

        return rows
    
    def get_user_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, avatar, company, country, budget FROM user WHERE id = ?", (id,))
        row = cursor.fetchone()
        return row

    