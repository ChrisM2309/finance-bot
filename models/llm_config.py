import os, sys
from openai import OpenAI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
import json
import faiss
import numpy as np
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
FEEDBACK_FILE = "models\\feedback_data\\chatbot_feedback.json"
TRAINING_FILE = "models\\fine_tuning_data\\training_data.jsonl"
FEEDBACK_LIMIT = 50
#MANEJO DE EMBEDDINGS PARA FEEDBACK 
EMBEDDING_MODEL = "text-embedding-ada-002"
dimension = 1536 
index = faiss.IndexFlatL2(dimension)
# Funcion para actualizar el fine tunning 
def prepare_fine_tunning_data():
    if not os.path.exists(FEEDBACK_FILE):
        return
    
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with open(TRAINING_FILE, "a", encoding="utf-8") as f:
        for entry in data:
            if entry["feedback"] == "like":
                f.write(json.dumps({
                        "messages": [
                            {"role": "system", "content": "Eres un asesor financiero experto para PYMES."},
                            {"role": "user", "content": entry["prompt"]},
                            {"role": "assistant", "content": entry["response"]}
                        ]
                    }, ensure_ascii=False) + "\n")
            elif entry["feedback"] == "dislike":
                f.write(json.dumps({
                    "messages": [
                        {"role": "system", "content": "Eres un asesor financiero experto de Ábaco para PYMES."},
                        {"role": "user", "content": entry["prompt"]},
                        {"role": "assistant", "content": "[EVITAR ESTA RESPUESTA:]" + entry["response"]}
                    ]
                }, ensure_ascii=False) + "\n")
                
    # Limpiar el archivo de retroalimentación después de generar el training file
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
                
# Inicializar el modelo de OpenAI
def get_openai_llm():
    return ChatOpenAI(
        model= FINE_TUNED_MODEL,
        api_key = openai_api_key,
        temperature=0.0
    )
    
# FUNCION PARA GENERAR EL EMBEDDING DE TEXTO 
def get_embedding(text):
    response = openai_client.embeddings.create(input = text, model = EMBEDDING_MODEL)
    return np.array(response.data[0].embedding, dtype = np.float32)

# FUNCION PARA GUARDAR FEEDBACK 
def save_feedback(prompt, response, feedback):
    data = []
    if os.path.exists(FEEDBACK_FILE):
        try: 
            with open(FEEDBACK_FILE, 'r', encoding = 'utf-8') as file:
                content = file.read().strip()
                if content:
                    data = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            data = []
                
    embedding = get_embedding(prompt).tolist()
    data.append({"prompt": prompt, "response": response, "feedback": feedback, "embedding": embedding})
    
    # INSERTAR EN FEEDBACK_FILE 
    with open(FEEDBACK_FILE, 'w', encoding= 'utf-8') as file: 
        json.dump(data, file, ensure_ascii= False, indent= 2)
    # FUTURO --> CONVERTIR FEEDBACK_FILE EN FINE TUNNING FILE 
    if len(data) >= FEEDBACK_LIMIT:
        prepare_fine_tunning_data()
        print("Limite alcanzado de feedback, generando {}")

# FUNCION PARA OBTENER FEEDBACK RELEVANTE 
def get_similar_feedback(prompt, k = 3):
    if not os.path.exists(FEEDBACK_FILE):
        return {"likes": [], "dislikes": []}
    
    data = []
    try: 
        with open(FEEDBACK_FILE, 'r', encoding = 'utf-8') as file:
            content = file.read().strip()
            if content:
                data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return {"likes": [], "dislikes": []}
    
    if not data:
        return {"likes": [], "dislikes": []}
    
    embeddings = np.array([entry["embedding"] for entry in data], dtype=np.float32)
    global index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    query_embedding = get_embedding(prompt)
    distances, indices = index.search(np.array([query_embedding]), k)
    
    likes = []
    dislikes = []
    for idx in indices[0]:
        entry = data[idx]
        if entry["feedback"] == "like":
            likes.append(entry["response"])
        elif entry["feedback"] == "dislike":
            dislikes.append(entry["response"])
    
    return {"likes": likes[:k], "dislikes": dislikes[:k]}


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
        {"role": "system", "content": "Eres un asesor financiero experto de la fintech Abaco enfocado en PYMES. Responde la pregunta del usuario usando la informacion dada y mencionando como Abaco puede ayudar. No olvides que debes ayudar al usuario en su pregunta"}
    ]
    
    # Añadir historial si existe
    if chat_history:
        for msg in chat_history:
                # Obtener el rol desde el tipo de mensaje de LangChain
                role = getattr(msg, 'type', 'user')  # Default a 'user' si no hay type
                if role == "human":
                    role = "user"
                elif role == "ai":
                    role = "assistant"
                messages.append({"role": role, "content": msg.content})
    
    # Buscar feedback similar
    feedback = get_similar_feedback(prompt)
    # Construir el mensaje del usuario
    user_content = f"Pregunta: {prompt}"
    if context:
        user_content += f"\nMarco Teorico, usa esta informacion como la base a tu respuesta: {context}"
    if feedback["likes"]:
        user_content += f"\nRespuestas bien valoradas, sigue este estilo: {', '.join(f"{like}" for like in feedback['likes'])}"
    if feedback["dislikes"]:
        user_content += f"\nRespuestas mal valoradas, evita seguir este estilo: {', '.join(f"{dislike}" for dislike in feedback['dislikes'])}"
    messages.append({"role": "user", "content": user_content})
    
    try:
        response = openai_client.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"GetCompletion -- Error al procesar la consulta: {str(e)}")

if __name__ == "__main__":
    print("Completed llm_config")