import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

def discovery_modelo():
    print("\n--- 🔍 Scanner ativado: Procurando modelo disponível na sua chave... ---")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    check_list = [
        "models/gemini-1.5-flash",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-pro"
    ]
    
    try:
        modelos_autorizados = [m.name for m in genai.list_models()]
        for modelo in check_list:
            if modelo in modelos_autorizados:
                print(f"✅ Link estabelecido com: {modelo}")
                return modelo
    except Exception as e:
        print(f"⚠️ Erro no scanner: {e}")
    
    print("⚠️ Nenhum modelo da lista encontrado, usando fallback padrão.")
    return "models/gemini-1.5-flash"

@tool
def consultar_pedido(id_pedido: int) -> str:
    """Consulta o banco de dados do ERP para descobrir o status de um pedido."""
    try:
        conn = sqlite3.connect("erp_mock.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cliente, produto, status, data_entrega FROM pedidos WHERE id = ?", (id_pedido,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            cliente, produto, status, data_entrega = resultado
            return f"Pedido {id_pedido}: O cliente {cliente} comprou um {produto}. Status: {status}. Entrega: {data_entrega}."
        return f"Não encontrei o pedido {id_pedido} no sistema."
    except Exception as e:
        return f"Erro no banco: {str(e)}"


modelo_ativo = discovery_modelo()
llm = ChatGoogleGenerativeAI(model=modelo_ativo, temperature=0)
agente_erp = create_react_agent(llm, [consultar_pedido])

print("===================================================")
print("🤖 Agente ERP Online. (Digite 'sair' para encerrar)")
print("===================================================")

while True:
    pergunta_usuario = input("\nVocê: ")
    if pergunta_usuario.lower() in ['sair', 'exit', 'quit']:
        break
        
    print("Processando...")
    try:
        estado_final = agente_erp.invoke({"messages": [HumanMessage(content=pergunta_usuario)]})
        conteudo = estado_final["messages"][-1].content
        
        resposta_ia = conteudo[0].get('text', str(conteudo[0])) if isinstance(conteudo, list) else conteudo
        print(f"Agente: {resposta_ia}")

    except Exception as e:
        print(f"❌ Erro na execução: {e}")
