# SUBIR DATOS A OPEN AI
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Inicializa el cliente de OpenAI con tu clave API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Asegúrate de que la clave esté en tu .env

# Subir el archivo
with open("models\\fine_tuning_data\\training_data.jsonl", "rb") as file:
    response = client.files.create(
        file=file,
        purpose="fine-tune"
    )

file_id = response.id
print(f"Archivo subido con ID: {file_id}")

def get_training_file_id():
    return file_id
# INICIAR FINE TUNNING
# MONITOREAR