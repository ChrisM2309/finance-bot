from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI


chat = ChatOpenAI(model="gpt-4o-mini")

# RESPONDER PREGUNTAS FINANCEIRAS
prompt_preguntas = PromptTemplate(
    input_variables=["input"],
    template="""
    ERES UN ASESOR FINANCIERO EXPERTO
    Responde la siguiente pregunta financiera de manera clara y sencilla:
    "{input}"
    Usa toda la informacion disponible para responder la pregunta. 
    Si es necesarios, debes consultar la memoria para obtener datos relevantes.
    """
)
chain_preguntas = LLMChain(llm=chat, prompt=prompt_preguntas)

tool_preguntas = Tool(
    name="responder_preguntas_financieras",
    func=lambda x: chain_preguntas.run(input=x),
    description="Responder preguntas relacionadas a finanzas, dinero, manejo del negocio o similares"
)