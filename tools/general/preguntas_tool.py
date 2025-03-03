import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.tools import Tool
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

#CONECTAR CON EL VECTOR STORE
embeddings = OpenAIEmbeddings(openai_api_key= os.getenv("OPENAI_API_KEY"))
# VECTOR STORE LOCAL Y CARGADO 
abacoweb_vectorstore = FAISS.load_local(
    folder_path="./data/db/faiss",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)
#CREAR EL RETRIEVER ADECUADO DE ABACOWEB_VECTORSTORE

#CHAIN PARA DETERMINAR LA COMPLEJIDAD DE LA PREGUNTA
determinar_complejidad_prompt = PromptTemplate(
    input_variables=["input"],  
    template="""
    ERES UN EXPERTO EN ANALISIS DE TEXTO
    Determina la complejidad de la pregunta:
    {input}
    Clasificala como: 
    "simple": preguntas cortas y directas 
    "moderada": preguntas que requieren analisis, explicaciones o ejemplos
    "compleja": preguntas que requieren analisis profundo, pasos multiples, explicaciones detalladas o ejemplos extensos
    Devuelve solo la clasificacion (una palabra): simple, moderada o compleja
    """
)
determinar_complejidad_chain = LLMChain(llm=chat, prompt=determinar_complejidad_prompt)
# Amount of documents segun complejidad
num_documents_simple = 3
num_documents_moderada = 5
num_documents_compleja = 12

# Funcion para determinar la complejidad de la pregunta
def obtener_retriever_correcto(input_text):
    complejidad =  determinar_complejidad_chain.run(input=input_text)
    #print(f"Complejidad: {complejidad}" )
    if complejidad == "simple":
        retriever =  abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_simple})
        chain_type = "stuff"
    elif complejidad == "moderada":
        b_retriever = abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_moderada})
        compressor = LLMChainExtractor.from_llm(llm=chat)
        retriever = ContextualCompressionRetriever(
            base_compressor = compressor,
            base_retriever = b_retriever
        )
        chain_type = "stuff"
    else: #compleja
        retriever =  abacoweb_vectorstore.as_retriever(search_kwargs={"k": num_documents_compleja})
        chain_type = "map_reduce" 
    # Configura el RetrievalQA para usar el vector store
    return RetrievalQA.from_chain_type(
    llm=chat,
    chain_type= chain_type,
    retriever= retriever,
    return_source_documents=True
    )

# RESPONDER PREGUNTAS FINANCEIRAS
prompt_preguntas = PromptTemplate(
    input_variables=["input", "answer"],
    template="""
    ERES UN ASESOR FINANCIERO EXPERTO
    Responde la siguiente pregunta financiera de manera clara y sencilla:
    
    Texto: "{input}"
    
    Esta es la respuesta de la web de Abaco a la pregunta:
    ESTA ES LA INFORMACION CON QUE DEBES RESPONDER 
    Prioriza en todo momento usar la información del marco teórico de la web de Abaco para fundamentar tu respuesta.

    answer: {answer}
    
    Complementa la respuesta on tu conocimiento general e indica que lo hiciste. 
    Indica donde tomas la informacion (Abaco o informacion general)
    """
)
chain_preguntas = LLMChain(llm=chat, prompt=prompt_preguntas)

# Chain para formatear la respuesta
format_answer_prompt = PromptTemplate(
    input_variables=["input", "answer"],
    template = '''
    **Saludo:**
    (Elabora un saludo sencilla) 
    Para responder a la pregunta: "{input}"

    **Explicación de conceptos clave:**
    A continuación, te explico los conceptos fundamentales relacionados con tu pregunta.

    **Explicación paso a paso de la respuesta:**
    {answer}
    Si answer no tiene informacion o no hay informacion en la web de Abaco. Indica esto "No hay informacion en la web abaco, proporcionando una respuesta general..." y proporciona una respuesta general
    Agrega una explicación detallada de la respuesta

    **Ejemplo / Aplicación en la vida real:**
    Si hay sufciente informacion en la respuesta, genera un ejemplo:
    Por ejemplo, imagina que tienes una PYME y aplicas esto así... (ejemplo segun necesario)

    **Conclusión:**
    En resumen, esto es lo que necesitas saber sobre tu consulta. [ideas principales de la respuesta]

    '''
    )
format_answer_chain = LLMChain(llm = chat, prompt = format_answer_prompt)

# Funcion para generar respuesta a preguntas financieras
def respuesta_abaco_data(input_text):
    # obtener el retrieval qa correcto
    retrieval_qa = obtener_retriever_correcto(input_text)
    # Usa RetrievalQA para obtener respuesta con información de Abaco
    result = retrieval_qa({"query": input_text})
    answer = result["result"]
    #print("RESULTADO DEL RETRIEVAL QA")
    #print("Answer:", answer)
    # Si no hay respuesta útil del vector store, usa el chain general
    answer = chain_preguntas.run(input=input_text, answer = answer)
    
    final_answer = format_answer_chain.run(input = input_text, answer = answer)
    return final_answer

# Crear la herramienta para responder preguntas financieras
tool_preguntas = Tool(
    name="responder_preguntas_financieras",
    func= respuesta_abaco_data,
    description="Responder preguntas relacionadas a finanzas, dinero, manejo del negocio o similares"
)

# TESTEO SI FUNCIONA 

# test_questions = [
#         #"¿Qué es el flujo de caja?",  # Simple
#         #"¿Cómo puedo calcular el flujo de caja de mi negocio?",  # Moderada
#     ]
# for question in test_questions:
#         print("\nPregunta:", question)
#         print(tool_preguntas(question))
# print("\ntest 2")
# text2 = "Cual es el rol de la planificación financiera dinámica en el contexto de tasas de interés altas?"
# print(text2)
# print(respuesta_abaco_data(text2))
