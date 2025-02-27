from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI


chat = ChatOpenAI(model="gpt-4o-mini")

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

chain_registrar = LLMChain(llm=chat, prompt=prompt_registrar)

tool_registrar = Tool(
    name="registrar_transaccion",
    func=lambda x: chain_registrar.run(input=x),
    description="Sirve para registrar un ingreso o gasto con tipo (Ingreso/Gasto), monto (número), categoria (texto) y descripcion (texto) (opcional).")
