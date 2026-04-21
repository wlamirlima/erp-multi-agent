import sqlite3

def init_db():
    conn = sqlite3.connect("erp_mock.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY,
            cliente TEXT,
            produto TEXT,
            status TEXT,
            data_entrega TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    if cursor.fetchone()[0] == 0:
        pedidos_mock = [
            (101, 'Empresa Alfa', 'Switch Cisco Nexus', 'Em Rota', '2026-04-22'),
            (102, 'Provedor Beta', 'Roteador MikroTik CCR2216', 'Atrasado', '2026-04-25'),
            (103, 'Gama Tech', 'Servidor Dell R740', 'Entregue', '2026-04-20')
        ]
        cursor.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?, ?)", pedidos_mock)
        conn.commit()

    conn.close()
    print("Banco de dados do ERP simulado criado com sucesso!")

if __name__ == "__main__":
    init_db()
