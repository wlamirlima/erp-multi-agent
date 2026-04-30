import os
import sqlite3
from dotenv import load_dotenv

# Importações para o RAG e Agentes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import google.generativeai as genai

# Carrega as chaves e ativa o rastreamento do LangSmith
load_dotenv()

# --- FUNÇÃO DE DESCOBERTA DE MODELO ---
def discovery_modelo():
    """Busca o modelo Gemini disponível na sua conta para evitar erro 404."""
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    modelos = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    # Prioriza o flash, se não achar, pega o primeiro disponível
    for m in modelos:
        if "gemini-1.5-flash" in m:
            return m
    return modelos[0] if modelos else "gemini-pro"

# --- CONFIGURAÇÃO DO RAG (Base de Conhecimento) ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Lê o manual técnico
with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()

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

# --- 4. INICIALIZAÇÃO DINÂMICA ---
modelo_disponivel = discovery_modelo()
print(f"✅ Usando modelo: {modelo_disponivel}")
print("✅ Infraestrutura LangSmith ativa!")

llm = ChatGoogleGenerativeAI(model=modelo_disponivel, temperature=0)
tools = [consultar_pedido, consultar_manual_tecnico]
agente_sistema = create_react_agent(llm, tools)

# --- 5. LOOP DE INTERAÇÃO ---
print("\n" + "="*50)
print("🤖 Sistema Multi-Agente Online!")
print("Pergunte sobre pedidos ou dúvidas técnicas (ou 'sair')")
print("="*50)

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit", "quit"]:
        break
    
    inputs = {"messages": [HumanMessage(content=pergunta)]}
    try:
        for output in agente_sistema.stream(inputs, stream_mode="updates"):
            for node, values in output.items():
                if "messages" in values:
                    print(f"\nAssistente: {values['messages'][-1].content}")
    except Exception as e:
        print(f"\n❌ Erro na resposta: {e}")