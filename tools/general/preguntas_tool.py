# tools/general/preguntas_tool.py
import sys
import os

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
from data.vector_store_getter import get_vectorstore
try:
    abacoweb_vectorstore = get_vectorstore()
except FileNotFoundError as e:
    print(f"Error: {e}. Asegúrate de ejecutar abacoweb_vectorstore_generator.py primero.")
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

# Cantidad de documentos según complejidad
num_documents_simple = 2
num_documents_moderada = 4
num_documents_compleja = 5

# Función para obtener el retriever correcto
def obtener_retriever_correcto(input_text):
    if abacoweb_vectorstore is None:
        raise FileNotFoundError("Vector store no está disponible. Genera el vector store primero.")
    
    complejidad = determinar_complejidad_chain.run(input=input_text).strip()
    print(f"Complejidad: {complejidad}")

    if complejidad == "simple":
        base_retriever = abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_simple})
        chain_type = "stuff"
        return RetrievalQA.from_chain_type(
            llm=chat,
            chain_type=chain_type,
            retriever=base_retriever,
            return_source_documents=True
        )
    elif complejidad == "moderada":
        base_retriever = abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_moderada})
        chain_type = "stuff"
    else:  # compleja
        base_retriever = abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_compleja})
        chain_type = "map_reduce"

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
    multi_retriever_chain = LLMChain(llm=chat, prompt=multi_retriever_prompt)
    print(multi_retriever_chain.run(question=input_text))
    multi_retriever = MultiQueryRetriever(
        retriever=base_retriever,
        llm_chain=multi_retriever_chain
    )

    compressor = LLMChainExtractor.from_llm(chat)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=multi_retriever
    )

    return RetrievalQA.from_chain_type(
        llm=chat,
        chain_type=chain_type,
        retriever=compression_retriever,
        return_source_documents=True
    )

# Prompt para respuesta general (respaldo)
prompt_preguntas = PromptTemplate(
    input_variables=["input"],
    template="""
    ERES UN ASESOR FINANCIERO EXPERTO
    Responde la siguiente pregunta financiera de manera clara y sencilla:
    "{input}"
    Usa la información disponible del marco teórico de la web de Abaco para fundamentar tu respuesta.
    Si no encuentras información relevante, responde con tu conocimiento general.
    """
)
chain_preguntas = LLMChain(llm=chat, prompt=prompt_preguntas, memory=memory)

# Chain para formatear la respuesta
format_answer_prompt = PromptTemplate(
    input_variables=["input", "answer"],
    template='''
    **Saludo:**
    ¡Hola! Me alegra ayudarte con tu consulta financiera: "{input}"

    **Explicación de conceptos clave:**
    A continuación, te explico los conceptos fundamentales relacionados con tu pregunta.

    **Explicación paso a paso de la respuesta:**
    {answer}
    Si no hay información específica en la web de Abaco, indica: "No hay información específica en la web de Abaco, pero aquí tienes una respuesta general..." y complétala con conocimiento general.
    Si hay información de Abaco, prioriza usarla y complementa con conocimiento general si es necesario, indicando: "Basado en la web de Abaco y complementado con conocimiento general".

    **Ejemplo / Aplicación en la vida real:**
    Por ejemplo, imagina que tienes una PYME y aplicas esto así... (genera un ejemplo si hay suficiente información).

    **Conclusión:**
    En resumen, esto es lo que necesitas saber sobre tu consulta. [ideas principales de la respuesta]
    '''
)
format_answer_chain = LLMChain(llm=chat, prompt=format_answer_prompt)

# Función principal
def respuesta_abaco_data(input_text):
    retrieval_qa = obtener_retriever_correcto(input_text)
    result = retrieval_qa.invoke({"query": input_text})
    answer = result["result"]
    print("RESULTADO DEL RETRIEVAL QA")
    print("Answer:", answer)

    # Si no hay respuesta útil, usar chain_preguntas como respaldo
    if not answer or "No sé" in answer:
        answer = chain_preguntas.run(input=input_text)

    # Formatear la respuesta final
    final_answer = format_answer_chain.run(input=input_text, answer=answer)
    return final_answer

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