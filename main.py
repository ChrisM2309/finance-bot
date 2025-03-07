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



for i in range(5): 
    input_text = input("User: ")
    print("Bot: ", agente.run(input_text))
    print("\n")
