import os
import sqlite3
import warnings
import sys
import subprocess
import re
import time
from datetime import datetime
from itertools import cycle

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
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai

load_dotenv()

keys = [v for k, v in os.environ.items() if "GOOGLE_API_KEY" in k]
key_pool = cycle(keys)

def registrar_telemetria(thread_id, tokens, modelo):
    try:
        conn = sqlite3.connect("erp_mock.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetria_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                thread_id TEXT,
                modelo TEXT,
                tokens_consumidos INTEGER
            )
        """)
        cursor.execute("INSERT INTO telemetria_ia (timestamp, thread_id, modelo, tokens_consumidos) VALUES (?, ?, ?, ?)",
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), thread_id, modelo, tokens))
        conn.commit()
        conn.close()
    except:
        pass

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

if not os.path.exists("data/manuais.md"):
    sys.exit()

with open("data/manuais.md", "r", encoding="utf-8") as f:
    texto_manual = f.read()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
docs = text_splitter.create_documents([texto_manual])
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

@tool
def consultar_manual_tecnico(pergunta: str) -> str:
    """Consulta manuais técnicos para resolver problemas de redes e hardware."""
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
        return "Aviso: Não encontrado."
    except:
        return "Erro na consulta."

def descobrir_modelo_valido(api_key):
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods and "flash" in m.name.lower():
            return m.name
    return "models/gemini-1.5-flash"

def configurar_agente(api_key):
    modelo_full_path = descobrir_modelo_valido(api_key)
    llm = ChatGoogleGenerativeAI(model=modelo_full_path, google_api_key=api_key, temperature=0)
    tools = [consultar_pedido, consultar_manual_tecnico]
    return create_react_agent(llm, tools, checkpointer=MemorySaver()), modelo_full_path

instrucao = "Você é um Engenheiro de IA focado em automação técnica. Use as ferramentas diretamente e seja objetivo."
current_key = next(key_pool)
agente_sistema, nome_modelo = configurar_agente(current_key)

subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
print(f"✅ Link Estabilizado | Pool: {len(keys)} chaves | Modelo: {nome_modelo}")
print("-" * 55)

thread_id = "sessao_vaga_wlamir"
config = {"configurable": {"thread_id": thread_id}}
total_tokens_sessao = 0

while True:
    pergunta = input("\nVocê: ")
    if pergunta.lower() in ["sair", "exit"]:
        break
    
    sucesso = False
    while not sucesso:
        try:
            final_event = None
            for event in agente_sistema.stream(
                {"messages": [SystemMessage(content=instrucao), HumanMessage(content=pergunta)]}, 
                config=config, 
                stream_mode="values"
            ):
                last_msg = event['messages'][-1]
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    for call in last_msg.tool_calls:
                        print(f"⚙️  Agente Roteador: Acionando {call['name']}...")
                final_event = event
            
            if final_event:
                msg_obj = final_event['messages'][-1]
                
                if hasattr(msg_obj, 'usage_metadata') and msg_obj.usage_metadata:
                    usage = msg_obj.usage_metadata.get('total_token_count', 0)
                    total_tokens_sessao += usage
                    registrar_telemetria(thread_id, usage, nome_modelo)
                    print(f"--- [TELEMETRIA] Rodada: {usage} | Total Acumulado: {total_tokens_sessao} ---")
                
                txt = ""
                if isinstance(msg_obj.content, str): txt = msg_obj.content
                elif isinstance(msg_obj.content, list):
                    for p in msg_obj.content:
                        if isinstance(p, dict) and 'text' in p: txt += p['text']
                        elif isinstance(p, str): txt += p
                
                print(f"\nAssistente: {txt.strip()}")
                sucesso = True
                
        except Exception as e:
            if "429" in str(e) or "404" in str(e):
                print(f"🔄 Ajustando conexão e rotacionando chave...")
                current_key = next(key_pool)
                agente_sistema, nome_modelo = configurar_agente(current_key)
                time.sleep(1)
            else:
                print(f"❌ Erro: {e}")
                break