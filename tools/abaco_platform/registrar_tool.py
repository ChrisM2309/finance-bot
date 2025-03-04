import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool

# Importar memoria 
from memory.context import get_conversation_memory
memory = get_conversation_memory()

#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

# Crear una cadena (Chain) para registrar transacciones
prompt_registrar = PromptTemplate(
    input_variables=["input"],
    template=""""
    Del input recibido, analiza con precaucion y extrae los parametros necesarios para hacer el registro:
    - Tipo (Ingreso o Gasto)
    - Monto (número)
    - Categoría (texto)
    - Descripción (texto, opcional, usa '' si no está presente)

    Texto: "{input}"

    Devuelve la respuesta en formato "(tipo) registrado con (monto) en (categoria) con (descripcion).".
    """
)

chain_registrar = LLMChain(llm=chat, prompt=prompt_registrar, memory=memory)

tool_registrar = Tool(
    name="registrar_transaccion",
    func=lambda x: chain_registrar.run(input=x),
    description="Sirve para registrar un ingreso o gasto con tipo (Ingreso/Gasto), monto (número), categoria (texto) y descripcion (texto) (opcional).")

print("Registrar tool cargado")