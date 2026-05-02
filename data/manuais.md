import os
import sqlite3
import warnings

# --- 1. LIMPEZA TOTAL DE LOGS ---
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai

load_dotenv()

# --- 2. CONFIGURAÇÃO DO MODELO ---
def discovery_modelo():
    return "models/gemini-1.5-flash" # Estável e com cota gratuita alta

# --- 3. CONFIGURAÇÃO DO RAG (COM CHUNKING) ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()

# Fatiamos o manual para a busca ser cirúrgica
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
docs = text_splitter.create_documents([texto_manual])
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

@tool
def consultar_manual_tecnico(pergunta: str) -> str:
    """Consulta manuais técnicos para resolver problemas de redes."""
    docs = retriever.invoke(pergunta)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def consultar_pedido(termo: str) -> str:
    """Consulta pedidos por ID ou Nome do Cliente no banco ERP."""
    conn = sqlite3.connect("erp_mock.db")
    cursor = conn.cursor()
    if str(termo).isdigit():
        cursor.execute("SELECT id, cliente, produto, status FROM pedidos WHERE id = ?", (int(termo),))
    else:
        cursor.execute("SELECT id, cliente, produto, status FROM pedidos WHERE cliente LIKE ?", (f'%{termo}%',))
    res = cursor.fetchone()
    conn.close()
    if res:
        return f"Pedido {res[0]}: {res[1]} comprou {res[2]}. Status: {res[3]}"
    return "Pedido não encontrado."

# --- 4. INICIALIZAÇÃO ---
modelo_estavel = discovery_modelo()
print(f"✅ Modelo Ativo: {modelo_estavel}")

llm = ChatGoogleGenerativeAI(model=modelo_estavel, temperature=0)
tools = [consultar_pedido, consultar_manual_tecnico]
agente_sistema = create_react_agent(llm, tools)

# --- 5. LOOP DE INTERAÇÃO PROFISSIONAL ---
print("\n" + "="*50)
print("🤖 Sistema Multi-Agente Online!")
print("="*50)

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit"]:
        break
    
    inputs = {"messages": [HumanMessage(content=pergunta)]}
    try:
        # stream_mode="values" nos permite pegar apenas o estado final do chat
        for event in agente_sistema.stream(inputs, stream_mode="values"):
            pass 
        
        # Pegamos a última mensagem do evento final
        resposta_final = event['messages'][-1].content
        if resposta_final:
            print(f"\nAssistente: {resposta_final.strip()}")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")