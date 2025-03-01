import os
from openai import OpenAI
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI


# Configurar API de OpenAI
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar el cliente de OpenAI
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI(
    api_key = OPENAI_API_KEY
)
# Inicializar el modelo de OpenAI
def get_openai_llm():
    return  ChatOpenAI(model="gpt-4o-mini")