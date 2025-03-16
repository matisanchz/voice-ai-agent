from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Instantiate Model
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-3.5-turbo-1106",
)

def validate_name(name):
    # Prompt Template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You will recieve a name as an input. You must response with a 1 if it is a valid name, or a 0 if it an invalid name."),
            ("human", "{input}")
        ]
    )

    chain = prompt | llm

    return chain.invoke({"input": name}).content