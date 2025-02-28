import os
from openai import OpenAI as OpenAI

from fastapi import FastAPI
from pydantic import BaseModel

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.llms import OpenAI as OpenAI
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

