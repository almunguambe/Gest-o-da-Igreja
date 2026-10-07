import sqlite3
import os

banco_caminho = 'banco.db'
if not os.path.exists(banco_caminho):
    for f in os.listdir('.'):
        if f.endswith('.db'):
            banco_caminho = f
            break

print(f"Atualizando base de dados: {banco_caminho}")
conn = sqlite3.connect(banco_caminho)
cur = conn.cursor()

# Obter colunas existentes
cur.execute("PRAGMA table_info(membros);")
existentes = [r[1].lower() for r in cur.fetchall()]
print(f"Colunas atuais: {existentes}")

colunas_necessarias = [
    ("batizado", "VARCHAR(20) DEFAULT 'Não'"),
    ("data_batismo", "VARCHAR(50)"),
    ("igreja", "VARCHAR(150) DEFAULT 'IEAD Chicuque'"),
    ("status", "VARCHAR(50) DEFAULT 'Ativo'"),
    ("telefone", "VARCHAR(50)"),
    ("bairro", "VARCHAR(100)"),
    ("endereco", "TEXT"),
    ("naturalidade", "VARCHAR(100)"),
    ("filiacao", "VARCHAR(255)"),
    ("tipo_doc", "VARCHAR(50)"),
    ("num_doc", "VARCHAR(100)"),
    ("segmento", "VARCHAR(50)"),
    ("ano_conversao", "VARCHAR(50)"),
    ("cargo", "VARCHAR(100) DEFAULT 'Membro em Comunhão'"),
    ("departamento", "VARCHAR(100) DEFAULT 'Geral'"),
    ("foto_path", "VARCHAR(255)"),
    ("professor_nome", "VARCHAR(150)")
]

for col, tipo in colunas_necessarias:
    if col.lower() not in existentes:
        try:
            cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            print(f"  + Coluna adicionada: {col}")
        except Exception as e:
            print(f"  ! Falha ao adicionar {col}: {e}")

conn.commit()
conn.close()
print("✓ Base de dados sincronizada com sucesso!")