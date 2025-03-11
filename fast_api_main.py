import os
from openai import OpenAI as OpenAI

from fastapi import FastAPI
from pydantic import BaseModel

from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI as OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

# Importar save_feedback
from models.llm_config import save_feedback, prepare_fine_tunning_data

#prepare_fine_tunning_data()

import financebot
agente = financebot.get_agent() 

interaction_history = []

app = FastAPI()

class RequestData(BaseModel):
    text: str
class FeedbackData(BaseModel):
    feedback: str
class ResponseData(BaseModel):
    response: str

@app.post("/process", response_model=ResponseData)
async def process_text(data: RequestData):
    ai_response = agente.run(data.text) 
    interaction_history.append({"input": data.text, "response": ai_response})
    return ResponseData(response=ai_response)

@app.post("/feedback")
async def provide_feedback(data: FeedbackData):
    #obtener datos de la ultima iteraccion o prompt
    last_interaction = interaction_history[-1]
    user_input = last_interaction["input"]
    last_response = last_interaction["response"]

    if data.feedback.lower() == "regenerar":
        new_input = f"Aumenta temperatura y creatividad\nResponde: {user_input}"
        new_response = agente.run(new_input)
        interaction_history[-1]["response"] = new_response
        #retorna el id del prompt modificado y la nueva respuesta
        return {"interaction_id": len(interaction_history)-1, "new_response": new_response}

    # like y dislike
    if data.feedback.lower() in ["like", "dislike"]:
        save_feedback(user_input, last_response, data.feedback)
        return {"message": f"retroalimentacion '{data.feedback}' "}

    return {"error": "Invalid feedback option"}
