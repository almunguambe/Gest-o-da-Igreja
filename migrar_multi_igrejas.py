import sqlite3
import os

DATA_DIR = "/var/data" if os.path.exists("/var/data") else "."
DB_NAME = os.path.join(DATA_DIR, "gestao_chicuque.db")

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

print("--- A INICIAR MIGRACAO MULTI-CONGREGACAO ---")

# 1. Criar tabela igrejas se nao existir
c.execute('''
CREATE TABLE IF NOT EXISTS igrejas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    cidade TEXT,
    distrito TEXT,
    pastor TEXT,
    telefone TEXT,
    ativa INTEGER DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 2. Inserir a congregação de Chicuque como ID 1 caso nao exista
c.execute("SELECT id FROM igrejas WHERE id = 1")
if not c.fetchone():
    c.execute("""
        INSERT INTO igrejas (id, nome, cidade, distrito, pastor, telefone, ativa)
        VALUES (1, 'Congregação de Chicuque', 'Maxixe', 'Maxixe', 'Pastor Local', '+258 84 000 0000', 1)
    """)
    print("✓ Congregação de Chicuque configurada como ID = 1")
else:
    print("✓ Congregação de Chicuque já registada como ID = 1")

# 3. Lista de tabelas que precisam ter a coluna igreja_id
tabelas = [
    'usuarios',
    'membros',
    'financeiro',
    'transferencias',
    'casamentos',
    'mortes',
    'cultos_frequencia',
    'novos_convertidos',
    'patrimonio',
    'escalas',
    'campanhas_metas',
    'zonas_lista',
    'departamentos_lista',
    'categorias_financeiras'
]

for t in tabelas:
    try:
        c.execute(f"PRAGMA table_info({t})")
        colunas = [col[1] for col in c.fetchall()]
        if colunas and 'igreja_id' not in colunas:
            c.execute(f"ALTER TABLE {t} ADD COLUMN igreja_id INTEGER DEFAULT 1")
            print(f"✓ Coluna igreja_id adicionada a: {t}")
        else:
            print(f"- Tabela {t} já possui igreja_id ou ainda não foi criada.")
    except Exception as err:
        print(f"! Aviso na tabela {t}: {err}")

# 4. Adicionar is_superadmin à tabela usuarios
c.execute("PRAGMA table_info(usuarios)")
colunas_usuarios = [col[1] for col in c.fetchall()]
if 'is_superadmin' not in colunas_usuarios:
    c.execute("ALTER TABLE usuarios ADD COLUMN is_superadmin INTEGER DEFAULT 0")
    print("✓ Coluna is_superadmin adicionada à tabela usuarios")

# 5. Definir o utilizador admin como SuperAdmin
c.execute("UPDATE usuarios SET is_superadmin = 1, igreja_id = 1 WHERE usuario = 'admin'")

conn.commit()
conn.close()
print("--- MIGRACAO CONCLUIDA COM SUCESSO! ---")