import os
import sqlite3
import warnings

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
import google.generativeai as genai

load_dotenv()

def discovery_modelo():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    modelos = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    
    for m in modelos:
        if "gemini-3-flash" in m:
            return m
    return modelos[0] if modelos else "gemini-pro"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()
vectorstore = FAISS.from_texts([texto_manual], embeddings)
retriever = vectorstore.as_retriever()

@tool
def consultar_manual_tecnico(pergunta: str) -> str:
    """Consulta manuais técnicos para resolver problemas de redes."""
    docs = retriever.invoke(pergunta)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def consultar_pedido(termo: str) -> str:
    """Consulta pedidos por ID ou Nome do Cliente."""
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

modelo_fast = discovery_modelo()
print(f"✅ Modelo Ativo: {modelo_fast}")

llm = ChatGoogleGenerativeAI(model=modelo_fast, temperature=0)
tools = [consultar_pedido, consultar_manual_tecnico]
agente_sistema = create_react_agent(llm, tools)

print("\n" + "="*50)
print("🤖 Sistema Multi-Agente Online!")
print("="*50)

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit"]:
        break
    
    inputs = {"messages": [HumanMessage(content=pergunta)]}
    try:
        for output in agente_sistema.stream(inputs, stream_mode="updates"):
            for node, values in output.items():
                if "messages" in values:
                    msg_obj = values['messages'][-1]
                    if hasattr(msg_obj, 'content') and msg_obj.content:
                        if isinstance(msg_obj.content, str):
                            print(f"\nAssistente: {msg_obj.content.strip()}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")