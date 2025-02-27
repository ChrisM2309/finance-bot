import os
from openai import OpenAI as OpenAI

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.llms import OpenAI as OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

import json

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI(
    api_key = OPENAI_API_KEY
)

#ChatBot Type
chat = ChatOpenAI(model="gpt-4o-mini")

# TOOLS
# REGISTRAR
import tools.registrar_tool as registrar_tool
tool_registrar = registrar_tool.tool_registrar
chain_registrar = registrar_tool.chain_registrar

# CALCULAR FLUJO DE CAJA
import tools.flujo_caja_tool as flujo_caja_tool 
tool_flujo_caja = flujo_caja_tool.tool_flujo_caja
chain_flujo_caja = flujo_caja_tool.chain_flujo_caja

#  PRESUPUESTO
import tools.presupuesto_tool as presupuesto_tool 
tool_presupuesto = presupuesto_tool.tool_presupuesto
chain_presupuesto = presupuesto_tool.chain_presupuesto

# PREGUNTAS FINANCIERAS 
import tools.preguntas_tool as preguntas_tool
tool_preguntas = preguntas_tool.tool_preguntas
chain_preguntas = preguntas_tool.chain_preguntas


# BLOQUEAR PREGUNTAS NO FINANCIERAS
import tools.bloquear_tool as bloquear_tool
tool_bloquear = bloquear_tool.tool_bloquear
chain_bloquear = bloquear_tool.chain_bloquear

# MANEJO DE DEUDAS
import tools.deudas_tool as deudas_tool 
tool_deudas = deudas_tool.tool_deudas

# CALCULO BALANCE GENERAL 
import tools.balance_general_tool as balance_general_tool
tool_balance = balance_general_tool.tool_balance

# PROCESAR MULTIPLES TOOLS 
import tools.multiples_tool as multiples_tool
tool_multiples = multiples_tool.tool_multiples


#! CONFIGURAR AL AGENTE 

memory = ConversationBufferMemory(memory_key="chat_history")

# Inicializar el agente
# Lista de herramientas
tools = [
    tool_registrar,
    tool_flujo_caja,
    tool_presupuesto,
    tool_preguntas,
    tool_multiples,
    tool_deudas,
    tool_balance,
    tool_bloquear
  ]

# Inicializar el agente
agente = initialize_agent(
    tools = tools,
    llm = chat,
    agent="conversational-react-description",
    #verbose=True,
    max_iterations = 10,
    memory = memory
    )


# Testeo del agente
#print(agente.run("Quiero registrar un pago de $30 en electricidad, uno de $40 en internet. Luego, tengo que registrar un ingreso de $100 en ventas. Luego, calcula el flujo de caja con los valores anteriores y por ultimo, asigna una deuda de $40 para el 20 de marzo de 2025"))

#print(agente.run("Registra un gasto de $150 en insumos y un ingreso de $200 en ventas."))
#print(agente.run("¿Qué es el flujo de caja?"))
#print(agente.run("Calcula el flujo de caja con ingresos de $500 y gastos de $300."))
#print(agente.run("Registra un gasto de $200 en publiicidad."))
#print(agente.run("Cuanto he gastado en total?"))
#print(agente.run("¿Qué es el flujo de caja?"))

#print(agente.run("Responde como pregunta financiera, dame un resumen de todas las operaciones que he realizado"))

#print(agente.run("Calcula el balance general de ingresos y gastos."))
