import os
from openai import OpenAI
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

#INICIAL 
# Configurar API de OpenAI
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Inicializar el cliente de OpenAI
os.environ["OPENAI_API_KEY"] = openai_api_key
client = OpenAI(
    api_key = openai_api_key
)

# Inicializar el modelo de OpenAI
def get_openai_llm():
    return ChatOpenAI(model="gpt-4o-mini")