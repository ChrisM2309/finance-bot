from openai import OpenAI
import os
from langchain.agents import initialize_agent

# Importar la memoria
from memory.context import get_conversation_memory
memory = get_conversation_memory()

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
    agent="chat-conversational-react-description",
    verbose=True,
    max_iterations = 15,
    memory = memory,
    handle_parsing_errors=True  # Maneja errores de parseo
    )

def get_agent():
    return agente

def get_agent_tools(): 
    return agent_tools
