import os
from openai import OpenAI as OpenAI

from fastapi import FastAPI
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI as OpenAI

import financebot
agente = financebot.get_agent()

app = FastAPI()

class RequestData(BaseModel):
    text: str

class ResponseData(BaseModel):
    response: str
    

@app.post("/process", response_model=ResponseData)
async def process_text(data: RequestData):
    ai_response = agente.run(data.text)  # Use your existing agent
    return ResponseData(response=ai_response)

