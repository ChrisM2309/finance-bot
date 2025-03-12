import os
from openai import OpenAI as OpenAI

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
def run_chatbot(): 
    print("Bienvenido al Chatbot Financiero de Abaco. ¿En qué puedo ayudarte?\nEscribe 'salir' para terminar.")
    while True: 
        user_input = input("User: ").strip()
        if user_input.lower() == 'salir':
            break
        
        # Ejecutar agente 
        response = agente.run(user_input)
        interaction_history.append({"input": user_input, "response": response})

        # Mostrar respuesta 
        print(f"Bot: {response}")
        
        # Mostrar opciones
        print("Opciones: 'like', 'dislike', 'regenerar'")
        feedback = input("Retroalimentacion: ").strip().lower()
        #! ESTA VARIABLE DEBE CAMBIARSE PARA SER TOMADA DEL MENSAJE DE LA API
        
        # Si no tomo ninguna opcion 
        if feedback not in ['like', 'dislike', 'regenerar']:
            continue
        # Si el usuario decidio regenerar 
        if feedback == "regenerar":
            new_input = f"Aumenta temperatura y creatividad\nResponde: {user_input}"
            new_response = agente.run(new_input)
            interaction_history[-1]["response"] = new_response
            print(f"Bot: {new_response}")
            #Mostrar nuevo feedback 
            print("Opciones: 'like' o 'dislike'")
            feedback = input("Retroalimentacion: ").strip().lower()

        # Like y Dislike
        if feedback in ["like", "dislike"]:
            last_interaction = interaction_history[-1]
            last_input = last_interaction["input"]
            last_response = last_interaction["response"] 
            # Funcion de save_feedback en llm_config
            save_feedback(last_input, last_response, feedback)
            print(f"Retroalimentacion guardada: {feedback}")
            
            
if __name__ == "__main__":
    run_chatbot()
