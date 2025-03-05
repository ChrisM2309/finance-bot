import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # FinanceBot/
DATA_DIR = BASE_DIR / "data" / "abaco_web"
PERSIST_DIR = BASE_DIR / "data" / "db" / "faiss"
persist_directory = str(PERSIST_DIR).strip()

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

if os.path.exists(persist_directory):
    vectorstore = FAISS.load_local(
        folder_path=persist_directory,
        embeddings=embeddings,
        allow_dangerous_deserialization=True  # Habilitar deserialización peligrosa
    )
    print("Vector store cargado desde y existe: ", persist_directory)

def get_vectorstore():
    return vectorstore