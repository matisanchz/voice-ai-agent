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
    TEMPERATURE: float = 0.3

    AUDIO_PATH: Optional[str] = f"{root}\\audio\\"
    CHROMA_DB_PATH: Optional[str] = f"{root}\\chroma\\"
    PDF_PATH: Optional[str] = f"{root}\\pdf\\"
    FLATICON_REPO: Optional[str] = "https://cdn-icons-png.flaticon.com/512/219/"
    FLATICON_REPO_NUM: int = 219953

    SESSION_ID_KEY_TEMPLATE: Optional[str] = "_SESSION_"

settings = Settings()