# 🤖 Agente ERP Inteligente com Orquestração LangGraph

Este projeto consiste em um **Agente de IA Autônomo (AI Agent)** integrado a um banco de dados relacional (ERP simulado). O sistema utiliza modelos de linguagem de última geração para interpretar solicitações em linguagem natural, decidir pela execução de ferramentas externas e processar dados estruturados de forma resiliente.

## 🏗️ Diferenciais do Projeto (Mentalidade de Infraestrutura)

Diferente de scripts simples de IA, este projeto foi construído com foco em **resiliência e disponibilidade**, aplicando conceitos de Redes e TI no desenvolvimento de software:

* **Discovery Dinâmico de Modelos (Scanner):** Implementação de uma lógica de "Handshake" que realiza o scanner dos modelos disponíveis na chave de API do Google. Isso garante o funcionamento contínuo (failover) mesmo que um modelo específico esteja indisponível ou sem cota.
* **Padrão ReAct (Reason + Act):** O agente utiliza raciocínio lógico para decidir, de forma autônoma, quando deve acionar o banco de dados via **Tool Calling**.
* **Orquestração via LangGraph:** Utilização de grafos de estado para gerenciar o fluxo de conversação, permitindo que a IA mantenha o contexto e execute loops de consulta e resposta de forma estruturada.



## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.13
* **Framework de Agentes:** LangChain & LangGraph (Stateful Multi-Actor Applications).
* **Cérebro (LLM):** Google Gemini 1.5 Flash / 2.0 (via Google AI Studio).
* **Banco de Dados:** SQLite (ERP Mock).
* **Bibliotecas Auxiliares:** `google-generativeai`, `python-dotenv`.

## 📂 Estrutura do Repositório

* `main.py`: Núcleo do agente com lógica de auto-discovery, definição de ferramentas e loop de chat.
* `erp_mock.db`: Base de dados SQLite simulando registros de clientes e pedidos.
* `.env`: Configurações de ambiente (Chaves de API).
* `requirements.txt`: Lista de dependências para fácil instalação.

## 🚀 Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/erp-multi-agent.git](https://github.com/seu-usuario/erp-multi-agent.git)
    cd erp-multi-agent
    ```

2.  **Configure suas variáveis de ambiente:**
    Crie um arquivo `.env` na raiz e adicione sua chave de API:
    ```env
    GOOGLE_API_KEY=sua_chave_aqui
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicie o Agente:**
    ```bash
    python main.py
    ```

---
**Conectando Redes e IA:** Este projeto reflete a aplicação de conceitos de infraestrutura (como redundância e descoberta de serviços) no desenvolvimento de soluções modernas de Inteligência Artificial Generativa.