import sys
import os
import json
import re
import io
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

#Direccion
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configurar sys.stdout para usar UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Importar configuración del LLM
import models.llm_config as llm_config
chat = llm_config.get_openai_llm()

# Lista de herramientas para el prompt
lista_herramientas = []

# AGREGAR TOOLS 
import active_tools
agent_tools = active_tools.get_tools()

tools_in_financebot = []
for tool in agent_tools:
    tools_in_financebot.append(tool)
    lista_herramientas.append(tool.name)

# Prompt para descomponer el texto
prompt_descomponer = PromptTemplate(
    input_variables=["input", "lista_herramientas"],
    template="""
    Analiza el siguiente texto y descompónlo en una lista de tareas a ejecutar. Para cada tarea, identifica:
    - Herramienta a usar: Debe ser una de las siguientes: {lista_herramientas}.
    - Input específico para esa herramienta (como texto con indicaciones para ejecutar).

    Texto: "{input}"
    Herramientas disponibles: {lista_herramientas}

    Devuelve el resultado como una lista de objetos JSON válido, donde cada objeto tiene:
    - "tool": nombre de la herramienta a usar.
    - "input": texto con la indicación para la ejecución de la herramienta.

    Asegúrate de que el output sea un JSON válido. Solo devuelve el JSON, sin texto adicional.

    Ejemplo:
    Input: "Registra un ingreso de $100 en ventas y calcula el flujo de caja con ingresos de $500 y gastos de $300."
    Output:
    [
        {{"tool": "tool_registrar", "input": "Registra un ingreso de $100 en ventas."}},
        {{"tool": "tool_flujo_caja", "input": "Calcula el flujo de caja con ingresos de $500 y gastos de $300."}}
    ]
    """
)

# Chain para descomponer
chain_descomponer = LLMChain(llm=chat, prompt=prompt_descomponer)

# Función para parsear la respuesta del LLM
def parsear_respuesta_json(respuesta_llm):
    try:
        json_match = re.search(r'\[.*\]', respuesta_llm, re.DOTALL)
        if not json_match:
            raise ValueError("No se encontró un JSON válido en la respuesta del LLM.")
        json_str = json_match.group()
        #print("JSON extraído:", json_str)  # Para depuración
        tareas = json.loads(json_str)
        return tareas
    except (AttributeError, json.JSONDecodeError, ValueError) as e:
        print(f"Error al parsear el JSON: {e}")  # Para depuración
        return None

# Función para procesar múltiples herramientas
def procesar_multiples_tool(input_text):
    tareas_json = chain_descomponer.run(input=input_text, lista_herramientas=lista_herramientas)
    #print("RESULTADO DE CHAIN DESCOMPONER:", tareas_json)  # Para depuración
    
    tareas = parsear_respuesta_json(tareas_json)
    if not tareas:
        return "Error: No se pudo parsear la respuesta del LLM como JSON."
    
    #print("TAREAS PARSEADAS:", tareas)  # Para depuración
    
    resultados = []
    for tarea in tareas:
        tool_name = tarea.get('tool')
        tool_input = tarea.get('input')
        
        if not tool_name or not tool_input:
            resultados.append(f"Error: Tarea incompleta: {tarea}")
            continue
        
        cur_tool = next((t for t in tools_in_financebot if t.name == tool_name), None)
        if cur_tool is None:
            resultados.append(f"No se encontró la herramienta {tool_name}")
        else:
            try:
                resultados.append(cur_tool(tool_input))
            except Exception as e:
                resultados.append(f"Error al ejecutar la herramienta {tool_name}: {str(e)}")
    
    return "\n".join(resultados)

# Instancia de tool
tool_multiples = Tool(
    name="procesar_multiples",
    func=procesar_multiples_tool,
    description="Procesa un mensaje con múltiples instrucciones y ejecuta las herramientas en orden."
)

# Probar la función
#print(procesar_multiples_tool(input_text="Registra un ingreso de $100 en ventas y calcula el flujo de caja con ingresos de $500 y gastos de $300"))