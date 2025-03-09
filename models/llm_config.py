import os
from openai import OpenAI
#from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

#INICIAL 
# Configurar API de OpenAI
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Inicializar el cliente de OpenAI
os.environ["OPENAI_API_KEY"] = openai_api_key
openai_client = OpenAI(api_key=openai_api_key)
#client = OpenAI(
#    api_key = openai_api_key
#)
FINE_TUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:competitivecodingclub::B8pU9GKP"

# Inicializar el modelo de OpenAI
def get_openai_llm():
    return ChatOpenAI(
        model= FINE_TUNED_MODEL,
        api_key = openai_api_key
    )

# Función para usar chat completions directamente
def get_chat_completion(prompt, context=None, chat_history=None, temperature=0.0, max_tokens=500):
    """
    Genera una respuesta usando el endpoint /v1/chat/completions con el modelo ajustado.
    
    Args:
        prompt (str): La pregunta o instrucción del usuario.
        context (str, optional): Contexto adicional (ej. del vector store).
        chat_history (list, optional): Lista de mensajes previos para incluir historial.
        temperature (float): Controla la creatividad (0.0 = determinista).
        max_tokens (int): Límite de tokens en la respuesta.
    
    Returns:
        str: Respuesta generada por el modelo.
    """
    messages = [
        {"role": "system", "content": "Eres un asesor financiero experto de la fintech Abaco enfocado PYMES."}
    ]
    
    # Añadir historial si existe
    if chat_history:
        messages.extend([{"role": msg.type, "content": msg.content} for msg in chat_history])
    
    # Construir el mensaje del usuario
    user_content = prompt
    if context:
        user_content = f"Usa este contexto de la web de Ábaco: '{context}'. Responde: '{prompt}'"
    messages.append({"role": "user", "content": user_content})
    
    response = openai_client.chat.completions.create(
        model=FINE_TUNED_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    #print(messages)
    return response.choices[0].message.content



if __name__ == "__main__":
    print("Completed llm_config")