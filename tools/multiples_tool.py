from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
import json

chat = ChatOpenAI(model="gpt-4o-mini")

#IMPORTAR LAS DEMAS TOOLS
from tools.balance_general_tool import chain_balance
from tools.bloquear_tool import chain_bloquear
from tools.flujo_caja_tool import chain_flujo_caja
from tools.preguntas_tool import chain_preguntas
from tools.presupuesto_tool import chain_presupuesto
from tools.registrar_tool import chain_registrar
from tools.deudas_tool import chain_deudas

lista_herramientas = [
    "registrar_transaccion",
    "calcular_flujo_caja",
    "configurar_presupuesto",
    "responder_pregunta",
    "manejar_deudas",
    "calcular_balance_general",
    "bloquear_pregunta"
]

prompt_descomponer = PromptTemplate(
    input_variables=["input", "lista_heramientas"],
    template="""
    Analiza el siguiente texto y descompónlo en una lista de tareas a ejecutar. Para cada tarea, identifica:
    - Herramienta a usar: "registrar_transaccion", "calcular_flujo_caja", "configurar_presupuesto",  "responder_pregunta". Obtenlo de la lista de tools actuales.
    - Input específico para esa herramienta (como texto con indicaciones para ejecutar)

    Texto: "{input}"
    Herramientas disponibles: "{lista_herramientas}"

    Para el output:
    Devuelve el resultado como una lista de objetos JSON, donde cada objeto tiene:
    "tool": nombre de la herramienta a usar
    "input": texto con la indicacion para la ejecucion de la herramienta, con todos los parametros para ejecutarla.

    Ejemplo:
    Input: "Registra un ingreso de $100 en ventas y calcula el flujo de caja con ingresos de $500 y gastos de $300."
    Output: [
        {{"tool": "registrar_transaccion", "input": "Registra un ingreso de $100 en ventas."}},
        {{tool": "calcular_flujo_caja", "input": "Calcula el flujo de caja con ingresos de $500 y gastos de $300."}}
    ]
    """
)
#chain para descomponer
chain_descomponer = LLMChain(llm=chat, prompt=prompt_descomponer)

#Funcion para la implementacion de tool
def procesar_multiples_tool(input_text):
    tareas_json = chain_descomponer.run(input=input_text, lista_herramientas = lista_herramientas)
    print(tareas_json)    
    try:
        tareas = json.loads(tareas_json)
        print(tareas)
    except json.JSONDecodeError as e:
        return f"Error al procesar las tareas: {str(e)}"

    herramientas = {
        "registrar_transaccion": lambda x: chain_registrar.run(input=x),
        "calcular_flujo_caja": lambda x: chain_flujo_caja.run(input=x),
        "configurar_presupuesto": lambda x: chain_presupuesto.run(input=x),
        "responder_pregunta": lambda x: chain_preguntas.run(input=x),
        "manejar_deudas": lambda x: chain_deudas.run(input=x),
        "bloquear_pregunta": lambda x: chain_bloquear.run(input=x),
        "calcular_balance_general" : lambda x : chain_balance.run(input=x)
        # Agrega más herramientas según sea necesario
    }
    resultados = []
    for tarea in tareas:
        tool_name = tarea["tool"]
        tool_input = tarea["input"]
        resultado = herramientas[tool_name](tool_input)
        resultados.append(resultado)
    return "\n".join(resultados)

#instancia de tool
tool_multiples = Tool(
    name="procesar_multiples",
    func=procesar_multiples_tool,
    description="Procesa un mensaje con múltiples instrucciones y ejecuta las herramientas en orden."
)
