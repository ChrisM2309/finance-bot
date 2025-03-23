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
    
# REGISTRAR
# import tools.abaco_platform.registrar_tool as registrar_tool
# tool_registrar = registrar_tool.tool_registrar
# tools_abaco.append(tool_registrar)

# CALCULAR FLUJO DE CAJA
# import tools.abaco_platform.flujo_caja_tool as flujo_caja_tool 
# tool_flujo_caja = flujo_caja_tool.tool_flujo_caja
# tools_abaco.append(tool_flujo_caja)

#  PRESUPUESTO
# import tools.abaco_platform.presupuesto_tool as presupuesto_tool 
# tool_presupuesto = presupuesto_tool.tool_presupuesto
# tools_abaco.append(tool_presupuesto)

# MANEJO DE DEUDAS
# import tools.abaco_platform.deudas_tool as deudas_tool 
# tool_deudas = deudas_tool.tool_deudas
# tools_abaco.append(tool_deudas)

# CALCULO BALANCE GENERAL 
# import tools.abaco_platform.balance_general_tool as balance_general_tool
# tool_balance = balance_general_tool.tool_balance
# tools_abaco.append(tool_balance)

#! CONFIGURAR AL AGENTE 
# Lista de herramientas

if es_cliente_abaco:
    agent_tools =  tools_abaco
else:
    agent_tools = tools_not_client

def get_tools():
    return agent_tools

