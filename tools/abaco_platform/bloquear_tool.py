import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool

#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

# RESPONDER PREGUNTAS FINANCEIRAS
prompt_preguntas = PromptTemplate(
    input_variables=["input"],
    template="""
    EVALUA LA SIGUIENTE QUERY, 
    SI NO TIENE NINGUNA RELACION AL MANEJO DE NEGOCIO, FINANZAS, DINERO, EMPRESAS
    SI NO TIENE RELACION CON EL NEGOCIO QUE SE ADMINISTRA
    EN ESTE CASO, DEBES RESPONDER: 
    "Esa pregunta no esta relacionada con ningun ambito del chatbot financiero, por favor intenta otra pregunta."
    
    Texto: "{input}"
    """
)
chain_bloquear = LLMChain(llm=chat, prompt=prompt_preguntas)

tool_bloquear = Tool(
    name="responder_preguntas_no_financieras",
    func=lambda x: chain_bloquear.run(input=x),
    description="Bloquear preguntas NO relacionadas a finanzas, dinero o el negocio"
)