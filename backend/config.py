import os
from dotenv import load_dotenv

# Ambil path relative ke parent directory (root folder uas-nlp-project)
# Karena file ini berada di backend/config.py, file .env berada di ../.env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", ".env")

load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "resume-cover-letter-analyzer")

def check_config():
    if not GROQ_API_KEY:
        print("Peringatan: GROQ_API_KEY belum dikonfigurasi di file .env")
    else:
        print("GROQ_API_KEY berhasil dimuat.")
        
    if LANGCHAIN_TRACING_V2.lower() == "true" and not LANGCHAIN_API_KEY:
        print("Peringatan: LANGCHAIN_TRACING_V2 aktif, tetapi LANGCHAIN_API_KEY belum dikonfigurasi.")
    elif LANGCHAIN_TRACING_V2.lower() == "true":
        print("LangSmith Tracing aktif.")

