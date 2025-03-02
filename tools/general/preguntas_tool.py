import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import Chroma


#IMPORTAR EL CHATBOT DE GPT 
import models.llm_config as llm_config
chat  = llm_config.get_openai_llm()

# SUBIENDO DOCUMENTOS
# Cargar y procesar documentos .docx de data/abaco_web
def load_abaco_web_docs():
    loader = DirectoryLoader(
        path='data/abaco_web',
        glob='**/*.docx',  # Carga solo archivos .docx
        loader_cls= UnstructuredWordDocumentLoader
    )
    documents = loader.load()

    # Divide los documentos en fragmentos manejables
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250
    )
    texts = text_splitter.split_documents(documents)

    # Crea el vector store con embeddings de OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_documents(texts, embeddings)

    return vector_store

# Inicializa el vector store al cargar el módulo
vector_store = load_abaco_web_docs()

# Configura el RetrievalQA para usar el vector store
retrieval_qa = RetrievalQA.from_chain_type(
    llm=chat,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

# RETRIEVAL DE INFORMACION
retrieval_qa = RetrievalQA.from_chain_type(
    llm=chat,
    chain_type="stuff",  # Usa "stuff" para combinar documentos relevantes
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),  # Devuelve los 3 documentos más relevantes
    return_source_documents=True  # Opcional, para depuración
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
input_text = "¿Cómo puedo calcular el flujo de caja de mi negocio?"
print(respuesta_abaco_data(input_text))

text2 = "Cual es el rol de la planificación financiera dinámica en el contexto de tasas de interés altas?"
print(respuesta_abaco_data(text2))