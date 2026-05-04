import os
import sqlite3
import warnings
import sys
import subprocess
import re

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai

try:
    from huggingface_hub.utils import disable_progress_bar
    disable_progress_bar()
except ImportError:
    pass

load_dotenv()

def discovery_modelo():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    try:
        modelos = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        for m in modelos:
            if "gemini-1.5-flash" in m:
                return m
        return modelos[0] if modelos else "models/gemini-1.5-flash"
    except Exception:
        return "models/gemini-1.5-flash"

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
docs = text_splitter.create_documents([texto_manual])
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

@tool
def consultar_manual_tecnico(pergunta: str) -> str:
    """Consulta manuais técnicos para resolver problemas de redes."""
    docs = retriever.invoke(pergunta)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def consultar_pedido(termo: str) -> str:
    """Consulta pedidos no banco ERP por ID numérico ou Nome do Cliente."""
    try:
        conn = sqlite3.connect("erp_mock.db")
        cursor = conn.cursor()
        
        apenas_numeros = re.sub(r'\D', '', str(termo))
        
        if apenas_numeros:
            cursor.execute("SELECT id, cliente, produto, status FROM pedidos WHERE id = ?", (int(apenas_numeros),))
        else:
            cursor.execute("SELECT id, cliente, produto, status FROM pedidos WHERE cliente LIKE ?", (f'%{termo}%',))
        
        res = cursor.fetchone()
        conn.close()
        if res:
            return f"RESULTADO_ERP: ID {res[0]} | Cliente: {res[1]} | Produto: {res[2]} | Status: {res[3]}"
        return f"AVISO: Nenhuma correspondência para '{termo}' no banco ERP."
    except Exception as e:
        return f"ERRO_SQL: {str(e)}"

nome_modelo = discovery_modelo()
subprocess.run("cls", shell=True)

print(f"✅ Link Estabilizado: {nome_modelo}")

llm = ChatGoogleGenerativeAI(model=nome_modelo, temperature=0)
tools = [consultar_pedido, consultar_manual_tecnico]

memory = MemorySaver()
agente_sistema = create_react_agent(llm, tools, checkpointer=memory)

print("\n" + "="*50)
print("🤖 Sistema Multi-Agente Online")
print("="*50)

config = {"configurable": {"thread_id": "sessao_vaga_ia"}}
total_tokens = 0

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit"]:
        break
    
    inputs = {"messages": [HumanMessage(content=pergunta)]}
    try:
        final_event = None
        for event in agente_sistema.stream(inputs, config=config, stream_mode="values"):
            final_event = event
        
        if final_event:
            msg_obj = final_event['messages'][-1]
            
            if hasattr(msg_obj, 'usage_metadata') and msg_obj.usage_metadata:
                usage = msg_obj.usage_metadata
                atual = usage.get('total_token_count', 0)
                total_tokens += atual
                print(f"--- [TELEMETRIA] Tokens: {atual} | Acumulado: {total_tokens} ---")

            conteudo = msg_obj.content
            if isinstance(conteudo, list):
                resposta_final = " ".join([str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in conteudo])
            else:
                resposta_final = str(conteudo)

            if resposta_final.strip():
                print(f"\nAssistente: {resposta_final.strip()}")
            
    except Exception as e:
        print(f"\n❌ Erro de Execução: {e}")