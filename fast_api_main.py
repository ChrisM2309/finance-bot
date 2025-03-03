import os
from openai import OpenAI as OpenAI

from fastapi import FastAPI
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI as OpenAI

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

app = FastAPI()

class RequestData(BaseModel):
    text: str

class ResponseData(BaseModel):
    response: str
    

@app.post("/process", response_model=ResponseData)
async def process_text(data: RequestData):
    query = format_query.format(user_input=data.text)
    ai_response = agente.run(query)  # Use your existing agent
    return ResponseData(response=ai_response)

