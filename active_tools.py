# SI ES CLIENTE DE ABACO 
# ESTO SERA MEJORADO LUEGO, PARA PROTOTIPO SERA BOOL 
es_cliente_abaco = False 
                   
# TOOLS
#? Tools generales
tools_general = [] 

# PREGUNTAS FINANCIERAS 
import tools.general.preguntas_tool as preguntas_tool
tool_preguntas = preguntas_tool.tool_preguntas
tools_general.append(tool_preguntas)

#* Tools de la plataforma de Abaco
tools_abaco = []
if es_cliente_abaco:
    # REGISTRAR
    import tools.abaco_platform.registrar_tool as registrar_tool
    tool_registrar = registrar_tool.tool_registrar
    tools_abaco.append(tool_registrar)

    # CALCULAR FLUJO DE CAJA
    import tools.abaco_platform.flujo_caja_tool as flujo_caja_tool 
    tool_flujo_caja = flujo_caja_tool.tool_flujo_caja
    tools_abaco.append(tool_flujo_caja)

    #  PRESUPUESTO
    import tools.abaco_platform.presupuesto_tool as presupuesto_tool 
    tool_presupuesto = presupuesto_tool.tool_presupuesto
    tools_abaco.append(tool_presupuesto)

    # MANEJO DE DEUDAS
    import tools.abaco_platform.deudas_tool as deudas_tool 
    tool_deudas = deudas_tool.tool_deudas
    tools_abaco.append(tool_deudas)

    # CALCULO BALANCE GENERAL 
    import tools.abaco_platform.balance_general_tool as balance_general_tool
    tool_balance = balance_general_tool.tool_balance
    tools_abaco.append(tool_balance)

#! CONFIGURAR AL AGENTE 
# Lista de herramientas
agent_tools = tools_general
if es_cliente_abaco:
    agent_tools = agent_tools + tools_abaco

def get_tools():
    return agent_tools

