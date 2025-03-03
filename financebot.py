from openai import OpenAI
import os
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

import json

# Importar la memoria
from memory.context import conversation_memory
memory = conversation_memory

#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
agent_model  = llm_config.get_openai_llm()


#Agent tools importar 
import active_tools
agent_tools = active_tools.get_tools()

# PROCESAR MULTIPLES TOOLS 
import tools.general.multiples_tool as multiples_tool
tool_multiples = multiples_tool.tool_multiples
agent_tools.append(tool_multiples)

# Inicializar el agente
agente = initialize_agent(
    tools = agent_tools,
    llm = agent_model,
    agent="conversational-react-description",
    #verbose=True,
    max_iterations = 25,
    memory = memory
    )

def get_agent():
    return agente

def get_agent_tools(): 
    return agent_tools


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
