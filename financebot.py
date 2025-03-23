from openai import OpenAI
import os
from langchain.agents import initialize_agent

# Importar la memoria
from memory.context import get_conversation_memory
memory = get_conversation_memory()

# IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
agent_model = llm_config.get_simple_openai_llm()

# Agent tools importar 
import active_tools
agent_tools = active_tools.get_tools()

# PROCESAR MULTIPLES TOOLS 
import tools.general.multiples_tool as multiples_tool
tool_multiples = multiples_tool.tool_multiples
agent_tools.append(tool_multiples)

from custom_executor_and_parser import CustomOutputParser

# Inicializar el agente
agente = initialize_agent(
    tools=agent_tools,
    llm=agent_model,
    agent="chat-conversational-react-description",
    verbose=True,
    max_iterations=30,
    memory=memory,
    handle_parsing_errors=True, # Maneja errores de parseo
    output_parser=CustomOutputParser()  # Agregar el parser personalizado aquí
)

from custom_executor_and_parser import CustomAgentExecutor

custom_executor = CustomAgentExecutor.from_agent_and_tools(
    agent=agente.agent,
    tools = agente.tools,
    memory = memory,
    verbose = True,
    max_iterationes = 20
)
def get_agent():
    return custom_executor

def get_agent_tools():
    return agent_tools