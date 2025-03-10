import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

import os, dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import openai

import models.llm_config as llm_config
chat = llm_config.get_openai_llm()

# Configurar PATH
# Definir la ruta absoluta a la raíz del proyecto
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # FinanceBot/
DATA_DIR = BASE_DIR / "data" / "abaco_web"
PERSIST_DIR = BASE_DIR / "data" / "db" / "faiss"
persist_directory = str(PERSIST_DIR).strip()


# Verificar si la carpeta existe
if not DATA_DIR.exists():
    raise FileNotFoundError(f"La carpeta '{DATA_DIR}' no existe. Asegúrate de que contenga archivos .docx.")

# 1. Subir documentos
loader = DirectoryLoader(
        path='./data/abaco_web',
        glob='**/*.docx',  # Carga solo archivos .docx
        loader_cls= UnstructuredWordDocumentLoader
    )

docs = loader.load()

# CHUNCK SIZE
chunk_size = 1000
chunk_overlap = int((0.4 * chunk_size)//1)
# 2.Split documents into manageable fragments
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = chunk_size,
    chunk_overlap = chunk_overlap
)
splits = text_splitter.split_documents(docs)

print("LEN DOCS", len(docs))
print("LEN SPLIT", len(splits))
print("CHUNK SIZE", chunk_size)
print("CHUNK OVERLAP", chunk_overlap)

# 2. Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# 3. GUARDAR EN VECTOR STORE

abacoweb_vectorstore = FAISS.from_documents(
    documents=splits,
    embedding= embeddings
)

abacoweb_vectorstore.save_local(persist_directory)
print("Vector store guardado en: ", persist_directory)



#vectorstore  FAISS.load_local(persist_directory)

''' 4. Retrieval QA 
retriever = abacoweb_vectorstore.as_retriever()
retriever_qa = "CUAL ES El rol de la planificación financiera dinámica en un contexto de tasas de interés altas"

retriever_docs = retriever.invoke(retriever_qa, k=3)
print(retriever_docs[0].page_content)
''' 
 


