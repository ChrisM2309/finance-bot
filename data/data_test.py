import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

import os, dotenv
from dotenv import load_dotenv, find_dotenv
import openai

import models.llm_config as llm_config
chat = llm_config.get_openai_llm()


# 1. Subir documentos
loader = DirectoryLoader(
        path='./data/abaco_web',
        glob='**/*.docx',  # Carga solo archivos .docx
        loader_cls= UnstructuredWordDocumentLoader
    )

docs = loader.load()

# 2.Split documents into manageable fragments
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 800,
    chunk_overlap = 150
)
splits = text_splitter.split_documents(docs)
print("LEN SPLIT", len(splits))

# 2. Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# 3. GUARDAR EN VECTOR STORE
persist_directory = "./data/db/faiss"

abacoweb_vectorstore = FAISS.from_documents(
    documents=splits,
    embedding= embeddings
)

abacoweb_vectorstore.save_local(persist_directory)

if os.path.exists(persist_directory):
    vectorstore = FAISS.load_local(
        folder_path=persist_directory,
        embeddings=embeddings,
        allow_dangerous_deserialization=True  # Habilitar deserialización peligrosa
    )
#vectorstore = FAISS.load_local(persist_directory)

''' 4. Retrieval QA 
retriever = abacoweb_vectorstore.as_retriever()
retriever_qa = "CUAL ES El rol de la planificación financiera dinámica en un contexto de tasas de interés altas"

retriever_docs = retriever.invoke(retriever_qa, k=3)
print(retriever_docs[0].page_content)
''' 
 


