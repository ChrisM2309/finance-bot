from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI(model="gpt-4o-mini")

#Chain para manejo de deudas

#Prompt de deudas
prompt_deudas = PromptTemplate(
    input_variables=["input"],
    template="""
    Del siguiente texto, extrae los parametros para manejar un deuda:
    - Acccion (agregar, pagar, consultar) o similares
    - Monto (número)
    - Plazo (número)
    - Acreedor (texto)
    - Interés (número, opcional)
    - Fecha de vencimiento (fecha)
    - Descripción (texto, opcional, usa '' si no está presente)

    Texto: "{input}"

    Devuelve la respuesta en formato:
    Segun la accion que se quiera realizar, devolver una respuesta diferente:
    - Agregar: "Deuda de $(monto) a (acreedor) con vencimiento (fecha_vencimiento) agregada" (Agregar 'interes' y otros parametros si existen)
    - Pagar: "Deuda de $(monto) a (acreedor) con vencimiento (fecha_vencimiento) pagada" (Agregar 'interes' y otros parametros si existen)
    - Consultar: "Lista de deudas: (lista_deudas)"
    """
)
def manejar_deudas_tool(input_text):
    return chain_deudas.run(input=input_text)\

#chain de deudas
chain_deudas = LLMChain(llm=chat, prompt=prompt_deudas)
tool_deudas = Tool(
    name = "manejar_deudas",
    func = manejar_deudas_tool,
    description = "Sirve para manejar deudas. Puede agregar, pagar o consultar deudas."
)
