# SI ES CLIENTE DE ABACO 
# ESTO SERA MEJORADO LUEGO, PARA PROTOTIPO SERA BOOL 
from is_client import get_is_abaco_client
es_cliente_abaco = get_is_abaco_client()
print(f"From active_tools, es cliente abaco = {es_cliente_abaco}")
                   
# TOOLS
#? Tools generales
tools_not_client = [] 

# PREGUNTAS FINANCIERAS 
import tools.general.preguntas_tool as preguntas_tool
tool_preguntas = preguntas_tool.tool_preguntas
tools_not_client.append(tool_preguntas)

#* Tools de la plataforma de Abaco
tools_abaco = []
if es_cliente_abaco:
    from tools.abaco_platform.abaco_client_tool import tool_abaco_client
    tools_abaco.append(tool_abaco_client)

#! CONFIGURAR AL AGENTE 
# Lista de herramientas

if es_cliente_abaco:
    agent_tools =  tools_abaco
else:
    agent_tools = tools_not_client

def get_tools():
    es_cliente_abaco = get_is_abaco_client()
    if es_cliente_abaco:
        agent_tools =  tools_abaco
    else:
        agent_tools = tools_not_client
    return agent_tools

