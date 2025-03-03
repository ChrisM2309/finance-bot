import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

#CONECTAR CON EL VECTOR STORE
embeddings = OpenAIEmbeddings(openai_api_key= os.getenv("OPENAI_API_KEY"))
abacoweb_vectorstore = FAISS.load_local(
    folder_path="./data/db/faiss",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)
#CREAR EL RETRIEVER DE ABACOWEB_VECTORSTORE
retriever = abacoweb_vectorstore.as_retriever(search_kwargs={"k": 5})

# Configura el RetrievalQA para usar el vector store
retrieval_qa = RetrievalQA.from_chain_type(
    llm=chat,
    chain_type="stuff",
    retriever= retriever,
    return_source_documents=True
)

# RESPONDER PREGUNTAS FINANCEIRAS
prompt_preguntas = PromptTemplate(
    input_variables=["input"],
    template="""
    ERES UN ASESOR FINANCIERO EXPERTO
    Responde la siguiente pregunta financiera de manera clara y sencilla:
    
    Texto: "{input}"
    
    Usa la información disponible del marco teórico de la web de Abaco para fundamentar tu respuesta.
    Si no encuentras información relevante, responde con tu conocimiento general.
    """
)
chain_preguntas = LLMChain(llm=chat, prompt=prompt_preguntas)

# Funcion para generar respuesta a preguntas financieras
def respuesta_abaco_data(input_text):
    # Usa RetrievalQA para obtener respuesta con información de Abaco
    result = retrieval_qa({"query": input_text})
    answer = result["result"]
    print("RESULTADO DEL RETRIEVAL QA")
    print("Answer:", answer)
    # Si no hay respuesta útil del vector store, usa el chain general
    if not answer or "No sé" in answer:
        return chain_preguntas.run(input=input_text)
    return answer

# Crear la herramienta para responder preguntas financieras
tool_preguntas = Tool(
    name="responder_preguntas_financieras",
    func= respuesta_abaco_data,
    description="Responder preguntas relacionadas a finanzas, dinero, manejo del negocio o similares"
)

# TESTEO SI FUNCIONA LA WEB DE ABACO

# input_text = "¿Cómo puedo calcular el flujo de caja de mi negocio?"
# print(input_text)
# print(respuesta_abaco_data(input_text))

# print("\ntest 2")
# text2 = "Cual es el rol de la planificación financiera dinámica en el contexto de tasas de interés altas?"
# print(text2)
# print(respuesta_abaco_data(text2))
