import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool

import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

prompt_presupuesto = PromptTemplate(
    input_variables=["input"],
    template="""
    Analiza el siguiente texto y extrae los parámetros para configurar un presupuesto:
    - Categoría (texto)
    - Monto (número)

    Texto: "{input}"

    Devuelve el resultado en formato: "✅ Presupuesto de $(monto) para (categoria) configurado."
    """
)

chain_presupuesto = LLMChain(llm=chat, prompt=prompt_presupuesto)

tool_presupuesto = Tool(
    name="configurar_presupuesto",
    func= lambda x: chain_presupuesto.run(input=x),
    description="Configura un presupuesto para una categoría."
)
