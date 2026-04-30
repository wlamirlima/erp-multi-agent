import sqlite3

def atualizar_banco():
    conn = sqlite3.connect("erp_mock.db")
    cursor = conn.cursor()

    # Limpa a tabela para não duplicar dados
    cursor.execute("DELETE FROM pedidos")

    # Dados focados em Provedores e Infraestrutura
    novos_pedidos = [
        (1, 'TechNorth Provedores', 'Lote 10x Switch Cisco Nexus 9300', 'Enviado'),
        (2, 'Cariri Conectividade', '500m Fibra Óptica Monomodo G.652D', 'Pendente'),
        (3, 'DataCenter Nordeste', 'Licença VMware vSphere Enterprise', 'Entregue'),
        (4, 'Sertão Telecom', 'Roteador MikroTik CCR2116-12G-4S+', 'Processando'),
        (5, 'Logística Express', 'Terminal Satelital ORBCOMM ST', 'Aguardando Pagamento'),
        (6, 'Prefeitura Municipal', 'Access Point Ubiquiti UniFi 6 Pro', 'Cancelado')
    ]

    cursor.executemany("INSERT INTO pedidos (id, cliente, produto, status) VALUES (?, ?, ?, ?)", novos_pedidos)
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados ERP atualizado com sucesso!")

if __name__ == "__main__":
    atualizar_banco()