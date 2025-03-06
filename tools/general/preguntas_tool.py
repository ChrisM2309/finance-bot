# tools/general/preguntas_tool.py
import sys
import os
import json 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever, MultiQueryRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Cargar variables de entorno
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Importar el chatbot y memoria
import models.llm_config as llm_config
chat = llm_config.get_openai_llm()
from memory.context import get_conversation_memory
memory = get_conversation_memory()

# Conectar con el vector store
# Conectar con el vector store usando el singleton de vector_store_getter.py
from data.vector_store_getter import get_vectorstore
try:
    abacoweb_vectorstore = get_vectorstore()  # Esto carga el vector store una sola vez
except FileNotFoundError as e:
    print(f"Error al cargar el vector store: {e}")
    abacoweb_vectorstore = None

# Chain para determinar la complejidad
determinar_complejidad_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
    ERES UN EXPERTO EN ANÁLISIS DE TEXTO
    Determina la complejidad de la pregunta:
    "{input}"
    Clasifícala como:
    - "simple": preguntas cortas y directas
    - "moderada": preguntas que requieren análisis, explicaciones o ejemplos
    - "compleja": preguntas que requieren análisis profundo, pasos múltiples o explicaciones detalladas
    Devuelve solo la clasificación: simple, moderada o compleja
    """
)
determinar_complejidad_chain = LLMChain(llm=chat, prompt=determinar_complejidad_prompt)

# CONFIGURACION DE RETRIEVER
RETRIEVER_CONFIG = {
    "simple": {"k": 2, "chain_type": "stuff", "use_multi_query": False},
    "moderada": {"k": 4, "chain_type": "stuff", "use_multi_query": True},
    "compleja": {"k": 5, "chain_type": "map_reduce", "use_multi_query": True}
}

#PROMPT PARA EL MULTI_RETRIEVER
multi_retriever_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
        ERES UN EXPERTO FINANCIERO
        Genera variaciones de esta pregunta financiera:
        "{question}"
        Incluye:
        1. Una reformulación directa como pregunta.
        2. Una pregunta relacionada con conceptos financieros generales.
        3. Una pregunta relacionadas a servicios o estrategias de Abaco para PYMES.
        4. Una pregunta relacionado a los conceptos clave de la pregunta original.
        Devuelve las variaciones en una lista, por ejemplo:
        ["¿Qué es el flujo de caja?", "¿Por qué es importante el flujo de caja en finanzas?", "¿Cómo apoya Abaco a las PYMES con el flujo de caja?"]
    """
    )

# Función para obtener el retriever correcto
def obtener_retriever_correcto(input_text):
    if abacoweb_vectorstore is None:
        raise FileNotFoundError("Vector store no está disponible. Genera el vector store primero.")
    
    #Obtener complejidad del prompt 
    complejidad = determinar_complejidad_chain.run(input=input_text).strip()
    print(f"Complejidad: {complejidad}")

    # Configuracion 
    config = RETRIEVER_CONFIG.get(complejidad, RETRIEVER_CONFIG["simple"])
    base_retriever = abacoweb_vectorstore.as_retriever(search_kwargs = {"k": config["k"]})

    if config["use_multi_query"]:
        multi_retriever_chain = LLMChain(llm = chat, prompt = multi_retriever_prompt)
        multi_retriever = MultiQueryRetriever(
            retriever=base_retriever,
            llm_chain=multi_retriever_chain
        )   
        compressor = LLMChainExtractor.from_llm(chat)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=multi_retriever
        )  
        retriever = compression_retriever   
    else: 
        retriever = base_retriever

    return RetrievalQA.from_chain_type(
        llm=chat,
        chain_type=config["chain_type"],
        retriever=retriever,
        return_source_documents=True
    )

# Prompt para respuesta general (respaldo)
prompt_preguntas = PromptTemplate(
    input_variables=["input"],
    template="""
    ERES UN ASESOR FINANCIERO EXPERTO
    Responde la siguiente pregunta financiera de manera clara y sencilla:
    "{input}"
    """
)
chain_preguntas = LLMChain(llm=chat, prompt=prompt_preguntas, memory=memory)

# Chain para formatear la respuesta
format_answer_prompt = PromptTemplate(
    input_variables=["input", "answer_ia", "answer_qa"],
    template='''
    RESPONDE SIGUIENDO ESTA PLANTILLA: 
    
    **Saludo:**
    ¡Hola! Me alegra ayudarte con tu consulta financiera: "{input}"

    **Explicación de conceptos clave:**
    A continuación, te explico los conceptos fundamentales relacionados con tu pregunta.

    **Explicación paso a paso de la respuesta:**
    INFORMACION DE ABACO - QA: {answer_qa}
    Respuesta de IA: {answer_ia}
    PRIORIZA LA INFORMACION DE ABACO EN TODO MOMENTO, usa la informacion IA para complementar si y solo si es necesario

    **Ejemplo / Aplicación en la vida real:**
    Por ejemplo, imagina que tienes una PYME y aplicas esto así... (genera un ejemplo si hay suficiente información).

    **Conclusión:**
    En resumen, esto es lo que necesitas saber sobre tu consulta. [ideas principales de la respuesta]
    '''
)
format_answer_chain = LLMChain(llm=chat, prompt=format_answer_prompt)

# Función principal
def respuesta_abaco_data(input_text):
    try: 
        retrieval_qa = obtener_retriever_correcto(input_text)
        result = retrieval_qa.invoke({"query": input_text})
        answer_qa = result["result"] if result["result"] else "No hay informacion especifica en la web de Abaco"
        print("RESULTADO DEL RETRIEVAL QA")
        print("Answer:", answer_qa)
        
        answer_ia = ""
        # Si no hay respuesta útil, usar chain_preguntas como respaldo
        if not answer_qa or "No sé" in answer_qa or "No hay informacion" in answer_qa: 
            answer_ia = chain_preguntas.run(input=input_text)
            answer_ia = f"Informacion general de IA: {answer_ia}"
            print("RESPUESTA DE IA", answer_ia)
        else:
            answer_ia = "Basado unicamente en la web de Abaco."
    # Formatear la respuesta final
        final_answer = format_answer_chain.run(input=input_text, answer_qa=answer_qa, answer_ia = answer_ia)
        return final_answer
    except Exception as e:
        return f"Lo siento, ocurrio un error al procesar la consulta: {str(e)}."
        

# Crear la herramienta
tool_preguntas = Tool(
    name="responder_preguntas_financieras",
    func=respuesta_abaco_data,
    description="Responder preguntas relacionadas a finanzas, dinero, manejo del negocio y similares"
)
print("Preguntas tool cargado")

# Testeo
if __name__ == "__main__":
    test_questions = [
        "¿Qué es el flujo de caja?",  # Simple
        "¿Cómo puedo calcular el flujo de caja de mi negocio?",  # Moderada
    ]
    for question in test_questions:
        print("\nPregunta:", question)
        print(tool_preguntas(question))