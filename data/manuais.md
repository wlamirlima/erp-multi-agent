# Base de Conhecimento Master - Engenharia de Redes & Infraestrutura

## 1. INFRAESTRUTURA DE DATA CENTER (CISCO NEXUS)
- **VPC (Virtual Port Channel)**: 
  - Para redundância, as interfaces devem estar em `channel-group X mode active`. 
  - Verifique o domínio com `show vpc`. O status deve ser `peer-keepalive-status: alive`.
- **Roteamento Estático e Dinâmico**:
  - `ip route 0.0.0.0/0 192.168.1.1` (Rota default).
  - OSPF: `router ospf 1` -> `network 10.0.0.0 0.0.0.255 area 0`.
- **Segurança FÍSICA**: Equipamentos Nexus consomem alta corrente. Verificar se a PDU suporta 20A por tomada antes da conexão.

## 2. PROVEDORES E BACKBONE (MIKROTIK ROUTEROS)
- **BGP AVANÇADO (Trânsito e Peering)**:
  - **Filtros de Entrada (Bogon Filters)**: Sempre descartar redes privadas (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) vindas de vizinhos BGP externos.
  - **Atributos**: Utilize `set-bgp-local-pref` para escolher o link de saída principal e `set-bgp-prepend` para influenciar o tráfego de entrada.
- **PPPoE Server**: 
  - MTU sugerido: `1480` ou `1492` para evitar fragmentação em túneis.
  - Authentication: Radius (Uso de User Manager ou sistema externo).
- **MPLS/VPLS**:
  - Utilizado para fechar túneis Camada 2 transparentes entre cidades. Requer LDP ativo nas interfaces de loopback.
- **QoS (Qualidade de Serviço)**:
  - `/queue simple` para controle de banda de clientes residenciais.
  - `/queue tree` para priorização de tráfego crítico (VoIP e Jogos).

## 3. REDES EXTERNAS E FIBRA ÓPTICA (FTTH/FUTURA)
- **Padrões GPON**:
  - Splitter 1:2 -> Perda de ~3.5dB.
  - Splitter 1:8 -> Perda de ~10.5dB.
  - Splitter 1:64 -> Perda total de ~18-20dB.
- **Troubleshooting de Fibra**:
  - "Luz Vermelha" na ONU: Geralmente rompimento físico ou conector sujo.
  - "PON piscando": Problema na autorização da OLT ou sinal abaixo de -27dBm.
- **Georeferenciamento**: Todos os elementos da rede (postes, caixas CTO, emendas) devem estar no Google Earth Pro (KMZ) com precisão de 3 metros para facilitar o trabalho da equipe de campo.

## 4. CONECTIVIDADE SATELITAL (INMET / ORBCOMM / STARLINK)
- **Terminais ORBCOMM ST-Série**:
  - **Configuração de Telemetria**: A taxa de reporte padrão é de 15 minutos. Para missões críticas, alterar para 5 minutos (consumo de bateria aumenta).
  - **Antena**: O ganho deve ser verificado via comando `AT+CSQ`. Valores abaixo de 12 indicam obstrução ou cabo danificado.
- **Starlink High Performance**:
  - Destinado a usuários corporativos e estações meteorológicas remotas.
  - **Aquecimento**: Em locais frios, ativar o modo "Snow Melt" para evitar acúmulo de gelo na parábola.
  - **Latência Esperada**: 25ms a 50ms em órbita baixa (LEO).

## 5. AUTOMAÇÃO, RPA E POWERSHELL
- **Integração Gemini + PowerShell**: 
  - Scripts para monitorar latência: `Test-NetConnection -ComputerName 8.8.8.8 -InformationLevel Detailed`.
- **UiPath (Processos ERP)**:
  - Se o bot falhar ao clicar em "Faturar", utilize o modo "Image Selection" com precisão de 0.8 se o seletor HTML não estiver disponível.
- **Python para Redes**: 
  - Biblioteca `Scapy` para análise de pacotes e `Paramiko` para automação via SSH em roteadores antigos que não suportam API.

## 6. POLÍTICAS DO ERP E LOGÍSTICA (SUNO TELECOM)
- **Ciclo de Vida do Pedido**:
  1. `Pendente`: Aguardando Financeiro.
  2. `Processando`: Estoque localizando e embalando.
  3. `Em Trânsito`: Postado ou em rota de entrega própria.
  4. `Entregue/Ativo`: Link instalado ou produto recebido.
- **Regras de Garantia**: 
  - Switches Nexus: 1 ano de garantia direta.
  - Rádios MikroTik: 6 meses (não cobre danos por surto elétrico ou raios).
- **SLA de Atendimento**: 
  - Clientes Gold (Links Dedicados): 4 horas para restabelecimento.
  - Clientes Standard (FTTH): 24 horas úteis.

# --- SEÇÃO DE INTELIGÊNCIA ANALÍTICA (IA OPTIMIZED) ---

## [POLÍTICAS DE DECISÃO TÉCNICA E PROBABILIDADES]
- **CENÁRIO: BGP State: Idle / Connect**
  - **85% de probabilidade**: Falta de rota (unreach) para o Peer IP. AÇÃO: Verificar `/ip route print`.
  - **15% de probabilidade**: Bloqueio de Firewall na porta TCP 179. AÇÃO: Verificar `chain=input` no MikroTik.
- **CENÁRIO: Sinal Óptico Alto (>-15dBm)**
  - **Diagnóstico**: Risco de queima do receptor óptico. AÇÃO: Instalar atenuador de 5dB ou 10dB imediatamente.

## [METADADOS DE HARDWARE E ESPECIFICAÇÕES (JSON-STYLE)]
- **ORBCOMM ST6100**: {"frequencia": "1626.5 – 1660.5 MHz", "io_interfaces": "4 Analógicas/Digitais", "alimentacao": "9 a 32V DC", "uso": "Logística e Estações INMET"}
- **MIKROTIK CCR2116-12G-4S+**: {"cpu": "16-core 2GHz", "ram": "16GB DDR4", "portas_10G": "4x SFP+", "perfil": "BGP Full Routing"}

## [MATRIZ SEMÂNTICA E SINÔNIMOS]
- **Trânsito IP** <-> **Link Dedicado** <-> **Upstream**
- **ONU** <-> **ONT** <-> **Modem da Fibra** <-> **CPE Óptica**
- **Luz Vermelha** <-> **LOS (Loss of Signal)** <-> **Sinal Rompido**