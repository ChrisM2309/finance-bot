from openai import OpenAI
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# IMPORTAR EL FILE ID DEL UPLOAD 
from fine_tuning_upload import get_training_file_id
training_file_id = get_training_file_id() 

# Crear el trabajo de fine-tuning
response = client.fine_tuning.jobs.create(
    training_file= training_file_id,  # Reemplaza con tu file_id
    model="gpt-4o-mini-2024-07-18",       # Modelo base
    hyperparameters={
        "n_epochs": 5         # Número de épocas (ajusta según necesidad)
    }
)

job_id = response.id
print(f"Trabajo de fine-tuning iniciado con ID: {job_id}")

def get_job_id():
    return job_id