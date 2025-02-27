from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI


chat = ChatOpenAI(model="gpt-4o-mini")

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