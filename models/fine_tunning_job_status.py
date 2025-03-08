from openai import OpenAI
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verificar el estado del trabajo
job_id = "ftjob-Ta0W0ZcNs0Yp0mgIFMMctoZU"
response = client.fine_tuning.jobs.retrieve(job_id)
print(f"Estado del trabajo: {response.status}")

# Si está completo, obtén el ID del modelo ajustado
if response.status == "succeeded":
    fine_tuned_model = response.fine_tuned_model
    print(f"Modelo ajustado creado: {fine_tuned_model}")