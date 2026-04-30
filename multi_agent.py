import os
import sqlite3
from dotenv import load_dotenv

# Importações para o RAG e Agentes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Carrega as chaves e ativa o rastreamento do LangSmith automaticamente
load_dotenv()

# --- CONFIGURAÇÃO DO RAG (Base de Conhecimento) ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Lê o manual que você criou na pasta data
with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()

# Cria o banco de dados de busca rápida na memória
vectorstore = FAISS.from_texts([texto_manual], embeddings)
retriever = vectorstore.as_retriever()

# --- FERRAMENTA 1: SUPORTE TÉCNICO (RAG) ---
@tool
def consultar_manual_tecnico(pergunta: str) -> str:
    """Consulta manuais técnicos para resolver problemas de redes ou dúvidas do ERP."""
    docs = retriever.invoke(pergunta)
    return "\n\n".join([doc.page_content for doc in docs])

# --- FERRAMENTA 2: VENDAS (SQL) ---
@tool
def consultar_pedido(id_pedido: int) -> str:
    """Consulta o status de um pedido no banco de dados ERP."""
    conn = sqlite3.connect("erp_mock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cliente, produto, status FROM pedidos WHERE id = ?", (id_pedido,))
    res = cursor.fetchone()
    conn.close()
    return f"Pedido {id_pedido}: {res[0]} comprou {res[1]}. Status: {res[2]}" if res else "Pedido não encontrado."

print("✅ Infraestrutura Multi-Agente e LangSmith ativos!")