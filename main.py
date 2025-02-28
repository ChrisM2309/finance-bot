import os
from openai import OpenAI as OpenAI

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.llms import OpenAI as OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

from financebot import agente 

for i in range(5): 
    input_text = input("User: ")
    print("Bot: ", agente.run(input_text))
    print("\n")
