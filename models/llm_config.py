import os
from openai import OpenAI
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI, OpenAI

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
FINE_TUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:competitivecodingclub::B8pU9GKP"

# Inicializar el modelo de OpenAI
def get_openai_llm():
    return ChatOpenAI(
        model= FINE_TUNED_MODEL,
        api_key = openai_api_key
    )
if __name__ == "__main__":
    print("Completed llm_config")