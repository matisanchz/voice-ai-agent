from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv(".env"))

root = Path(__file__).parent.parent

class Settings(BaseSettings):
    OPENAI_LLM_MODEL: Optional[str] = "gpt-3.5-turbo-1106"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    LANGCHAIN_VERBOSE: bool = False
    TEMPERATURE: int = 0

    AUDIO_PATH: Optional[str] = f"{root}\\audio\\"
    CHROMA_DB_PATH: Optional[str] = f"{root}\\chroma\\"
    CHAT_SESSIONS_PATH: Optional[str] = f"{root}\\chat_sessions\\"
    IMAGE_PATH: Optional[str] = f"images/"

settings = Settings()