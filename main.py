import os
from openai import OpenAI as OpenAI

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.llms import OpenAI as OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

import financebot
agente = financebot.get_agent() 

format_query = PromptTemplate(
    input_variables=['user_input'],
    template= ''' 
        SIEMPRE USAR UNA TOOL DISPONIBLE PARA RESPONDER LO SIGUIENTE: 
        LA TOOL POR DEFAULT ES TOOL_PREGUNTAS
        user_input: "{user_input}"
        SI NO HAY UNA TOOL DISPONIBLE, INDICAR QUE NO SABES RESPONDER A ESA CONSULTA, PEDIR MAS INFORMACION Y QUE SE VUELVA A INTENTAR
    '''
)

for i in range(5): 
    input_text = input("User: ")
    query = format_query.format(user_input=input_text)
    print("Bot: ", agente.run(query))
    print("\n")
