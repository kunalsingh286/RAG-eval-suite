import os
import re
import glob

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()  # loads OPENAI_API_KEY from .env

DATA_DIR = "data"
DB_DIR = "chroma_store"


# 1. LOAD ---- read text documents (e.g., Financial Reports)
def load_transcripts():

    docs = []
    for path in glob.glob(f"{DATA_DIR}/*.txt"):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Extract filename without extension to use as metadata
        doc_name = os.path.basename(path).replace(".txt", "")

        docs.append(Document(page_content=text, metadata={"session": doc_name}))

    return docs


# 2. BUILD ---- chunk, embed once, and keep it on disk so we don't re-embed
def load_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    if os.path.exists(DB_DIR):
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    docs = load_transcripts()

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    ).split_documents(docs)

    return Chroma.from_documents(chunks, embeddings, persist_directory=DB_DIR)


def build_retriever():
    return load_store().as_retriever(search_kwargs={"k": 5})


# 3. TRY IT ---- python src/retriever.py
if __name__ == "__main__":

    retriever = build_retriever()

    results = retriever.invoke("what are the main risk factors?")
    
    for r in results:
        print(f"[Source {r.metadata['session']}] {r.page_content[:150]}...\n")