# Base de Conhecimento Técnica - Engenharia de Redes

## Switch Cisco Nexus 9000 Series
- **Configuração de VLAN**: 
  1. Entre em modo global: `configure terminal`.
  2. Crie a VLAN: `vlan 100`.
  3. Nomeie (opcional): `name DATA_CENTER`.
- **Verificação de Interface**: Utilize `show interface status` para ver portas conectadas e velocidades.
- **Troubleshooting**: O comando `show logging last 20` exibe os últimos erros de sistema.

## MikroTik RouterOS (BGP & MPLS)
- **Acesso via Winbox**: Porta padrão 8291. Recomenda-se alterar em `/ip service`.
- **Configuração de BGP**:
  - Defina o ASN: `/routing bgp instance add name=default as=65000`.
  - Adicione Peer: `/routing bgp peer add name=ISP1 remote-address=10.0.0.1 remote-as=65001`.
- **Monitoramento em Tempo Real**: Utilize `/tool torch interface=ether1` para analisar o tráfego por protocolo e porta.

## Terminais Satelitais ORBCOMM (Série ST)
- **Substituição de Equipamento**: Certifique-se de que o cabo de antena está desconectado antes de remover a alimentação.
- **Provisionamento**: Após a instalação física, o terminal deve realizar o 'Handshake' com o satélite para baixar as tabelas de roteamento.

## Procedimentos Gerais de Suporte ERP
- **Status 'Processando'**: O item está em fase de separação no estoque físico.
- **Status 'Pendente'**: Aguardando a confirmação de crédito pelo departamento financeiro.
- **Política de Troca**: Equipamentos com lacre rompido não podem ser devolvidos sem laudo técnico prévio.