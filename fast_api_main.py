import os
from openai import OpenAI as OpenAI

from fastapi import FastAPI
from pydantic import BaseModel

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.llms import OpenAI as OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

from financebot import agente 

app = FastAPI()

class RequestData(BaseModel):
    text: str

class ResponseData(BaseModel):
    response: str

@app.post("/process", response_model=ResponseData)
async def process_text(data: RequestData):
    ai_response = agente.run(data.text)  # Use your existing agent
    return ResponseData(response=ai_response)

