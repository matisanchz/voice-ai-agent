import os
from config import settings
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from langchain_community.chat_message_histories.upstash_redis import UpstashRedisChatMessageHistory


load_dotenv()

history = UpstashRedisChatMessageHistory(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
    session_id="chat1",
    ttl=0
)

# Retriever
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

model = ChatOpenAI(model=settings.OPENAI_LLM_MODEL, temperature=settings.TEMPERATURE)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AtomChai voice assistant, capable to answer and guide leads. Answer the user's questions based on the chat history."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    chat_memory=history
)

def get_vectorstore():
    if not os.path.exists(settings.CHROMA_DB_PATH):
        os.makedirs(settings.CHROMA_DB_PATH)
        docs = get_documents_from_web('https://atomchat.io/acerca-de-nosotros/')
        print("ChromaDB created")
        return create_db(docs)
    else:
        print("ChromaDB loaded")
        return load_db()

def get_retriever():
    vectorStore = get_vectorstore()
    return vectorStore.as_retriever(search_kwargs={"k":2})
    

retriever = get_retriever()

search = TavilySearchResults()
retriever_tool = create_retriever_tool(
    retriever,
    "atomchat_web",
    "Use this tool when searching for information abour 'Atomchat.io'."
)
tools = [search, retriever_tool]

agent = create_openai_functions_agent(
    llm=model,
    prompt=prompt,
    tools=tools
)

agentExecutor = AgentExecutor(
    agent = agent,
    memory=memory,
    tools = tools
)

def process_chat(user_input):

    response = agentExecutor.invoke({
        "input": user_input
    })

    return response["output"]