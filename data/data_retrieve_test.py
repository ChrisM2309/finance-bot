import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import models.llm_config as llm_config
chat = llm_config.get_openai_llm()

embeddings = OpenAIEmbeddings(openai_api_key= os.getenv("OPENAI_API_KEY"))
abacoweb_vectorstore = FAISS.load_local(
    folder_path="./data/db/faiss",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)

retriever = abacoweb_vectorstore.as_retriever()
retriever_qa = "Cual es el rol de la planificación financiera dinámica en un contexto de tasas de interés altas"

retriever_docs = retriever.invoke(retriever_qa, k=3)
''' 
for doc in retriever_docs:
    print("SIGUIENTE DOCUMENTO")
    print(doc.page_content)
    print("\n")
'''