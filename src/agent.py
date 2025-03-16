import os
from config import settings
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories.upstash_redis import UpstashRedisChatMessageHistory

from database import ChromaDataBase, RedisDataBase
from utils import get_timestamp

load_dotenv()

class AgentManager:
    def __init__(self, session_key, user):
        self.session_key = session_key
        self.model = None
        self.history = None
        self.memory = None
        self.agent = None
        self.agent_executor = None

        self.init_model(user)

    def init_model(self, user):

        name, _ , company, country, budget = user

        self.model = ChatOpenAI(
            model=settings.OPENAI_LLM_MODEL, 
            temperature=settings.TEMPERATURE
        )

        self.history = UpstashRedisChatMessageHistory(
            url=os.getenv("UPSTASH_REDIS_REST_URL"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
            session_id = self.session_key,
            ttl=0
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an AtomChat voice assistant, capable to answer and guide leads. Answer the user's questions based on the chat history and your databse. In t his case, you are going to talk with {name}, which belongs to the company named {company} from the Country of {country}. Their budget is {budget}."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=self.history,
            key="history"
        )

        chroma = ChromaDataBase()

        retriever = chroma.get_retriever()

        search = TavilySearchResults()

        retriever_tool = create_retriever_tool(
            retriever,
            "atomchat_web",
            "Use this tool when searching for information abour 'Atomchat.io'."
        )
        
        tools = [search, retriever_tool]

        self.agent = create_openai_functions_agent(
            llm=self.model,
            prompt=prompt,
            tools=tools
        )

        self.agentExecutor = AgentExecutor(
            agent = self.agent,
            memory=self.memory,
            tools = tools
        )

    def get_chat_memory(self):
        memory_variables = self.memory.load_memory_variables({})
        
        chat_history = memory_variables.get("chat_history", [])
        
        return chat_history
        
    def process_chat(self, user_input):

        response = self.agentExecutor.invoke({
            "input": user_input
        })

        return response["output"]