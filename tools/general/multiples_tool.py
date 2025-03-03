import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
import json

import models.llm_config as llm_config
chat = llm_config.get_openai_llm()

#IMPORTAR LAS DEMAS TOOLS
from tools.abaco_platform.balance_general_tool import chain_balance
from tools.abaco_platform.bloquear_tool import chain_bloquear
from tools.abaco_platform.flujo_caja_tool import chain_flujo_caja
from tools.general.preguntas_tool import chain_preguntas
from tools.abaco_platform.presupuesto_tool import chain_presupuesto
from tools.abaco_platform.registrar_tool import chain_registrar
from tools.abaco_platform.deudas_tool import chain_deudas

# Lista de herramientas para el prompt 
lista_herramientas = []
# Tomar la lista de herramientas que tiene el agente actual
from financebot import agent_tools 
tools_in_financebot = agent_tools
for tool in tools_in_financebot:
    print(tool.name, tool.description) # Imprimir el nombre y la descripción de cada herramienta
    lista_herramientas.append(tool.name)
    
# Prompt para descomponer el texto
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
        "registrar_transaccion": chain_registrar.run,
        "calcular_flujo_caja": chain_flujo_caja.run,
        "configurar_presupuesto": chain_presupuesto.run,
        "responder_pregunta": chain_preguntas.run,
        "calcular_balance_general": chain_balance.run,
        "bloquear_cuenta": chain_bloquear.run,
        "manejar_deudas": chain_deudas.run
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
