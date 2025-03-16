import os
from config import settings

chat_sesions_path = settings.CHAT_SESSIONS_PATH

def get_chat_sessions():
    if not os.path.exists(chat_sesions_path):
        os.makedirs(chat_sesions_path)

    return ["new_session"] + os.listdir(settings.CHAT_SESSIONS_PATH)