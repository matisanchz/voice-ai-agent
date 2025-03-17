import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_message_histories.upstash_redis import UpstashRedisChatMessageHistory
from langchain.memory import ConversationBufferMemory

from config import settings
from database import ChromaDataBase, SQLDataBase
from utils import get_first_msg

load_dotenv()

class AgentManager():
    def __init__(self, session_key, user, first_msg):
        self.session_key = session_key
        self.first_msg = first_msg
        self.user = user
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
            ("system", f"Sos un asistente de voz de la empresa AtomChat.io, capaz de responder las preguntas de posibles clientes. Deberás responder todas las preguntas que el usuario haga, basandote tanto en la información que tenes como modelo, así como en las que se te va a dar a través de las tools, como bases de datos y el historial de chats. En este caso, hablarás con la persona cuyo nombre es {name}, perteneciente a la empresa {company} del país de {country}. Su presupuesto es {budget}. Será necesario que lo guíes en todo momento para que entienda sobre los servicios que podes ofrecer, según su presupuesto, así como los medios de pagos disponibles. Tienes PROHIBIDO responder con links externos. SIEMPRE responder en Español. En caso de que la persona te hable en otro idioma, o no se entiende su pregunta, por favor, responder cordialmente que vuelva a repetir su pregunta, ya que no se entiende. Cuando hables de números, transcribilos a letras. Por ejemplo, para el número 100, decir 'cien', y no uno, cero, cero, y así sucesivamente. También hablar en términos monetarios en dólares. Si las preguntas del usuario se alejan de lo que es AtomChat, recordar que sos un asistente de voz de AtomChat, y no deberías proporcionar información ajena a esta empresa. NUNCA menciones que no tienes acceso a información detallada; solo responde sobre los datos que tengas, y en caso de que el usuario necesite información más detallada, dirigirlo a la página 'atomchat.io'"),
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
            "Usa esta tool cuando sea necesario buscar información sobre la empresa 'Atomchat.io', sobre qué es, los servicios que ofrece, y sus medios de pago."
        )

        self.sql_db = SQLDataBase()
        sql_tool = QuerySQLDatabaseTool(db=self.sql_db.db)

        tools = [search, retriever_tool, sql_tool]

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

    def get_first_msg(self):

        self.first_msg = False

        msg = get_first_msg(self.user)

        self.memory.chat_memory.add_ai_message(msg)

        return msg

    def get_chat_memory(self):
        memory_variables = self.memory.load_memory_variables({})
        
        chat_history = memory_variables.get("chat_history", [])
        
        return chat_history
        
    def process_chat(self, user_input):

        response = self.agentExecutor.invoke({
            "input": user_input
        })

        return response["output"]