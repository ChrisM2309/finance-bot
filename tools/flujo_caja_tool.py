from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI(model="gpt-4o-mini")

# CALCULO DE FLUJO DE CAJA
prompt_flujo_caja = PromptTemplate(
    input_variables=["input"],
    template="""
    Analiza el siguiente texto y extrae los parámetros para calcular el flujo de caja:
    - Ingresos (número)
    - Gastos (número)

    Texto: "{input}"

    Calcula el saldo (ingresos - gastos) y devuelve el resultado en formato:
    "🔹 Ingresos: $(ingresos) 🔹 Gastos: $(gastos)🔹 Saldo: $(saldo)"
    """
)
chain_flujo_caja = LLMChain(llm=chat, prompt=prompt_flujo_caja)

tool_flujo_caja = Tool(
    name="calcular_flujo_caja",
    func=lambda x: chain_flujo_caja.run(input=x),
    description="Calcula el flujo de caja a partir de ingresos y gastos."
)
