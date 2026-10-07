import sqlite3
import os

# Importar o get_db diretamente do app para pegar a conexão real
from app import get_db, DATABASE_URL, psycopg2

print("Conectando à base de dados oficial do sistema...")
conn = get_db()
cur = conn.cursor() if hasattr(conn, 'cursor') else conn
is_pg = bool(DATABASE_URL and psycopg2)

colunas = [
    ("status", "VARCHAR(50) DEFAULT 'Ativo'"),
    ("batizado", "VARCHAR(20) DEFAULT 'Não'"),
    ("data_batismo", "VARCHAR(50)"),
    ("igreja", "VARCHAR(150) DEFAULT 'IEAD Chicuque'"),
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

if is_pg:
    print("Atualizando tabelas no PostgreSQL (Supabase)...")
    for col, tipo in colunas:
        try:
            cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
            conn.commit()
            print(f"✓ Coluna garantida: {col}")
        except Exception as e:
            try: conn.rollback()
            except Exception: pass
else:
    print("Atualizando tabelas no SQLite local...")
    cur.execute("PRAGMA table_info(membros);")
    existentes = [r[1].lower() for r in cur.fetchall()]
    print(f"Colunas existentes antes: {existentes}")
    
    for col, tipo in colunas:
        if col.lower() not in existentes:
            try:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                conn.commit()
                print(f"  + Coluna criada: {col}")
            except Exception as e:
                print(f"  ! Erro ao adicionar {col}: {e}")

if hasattr(conn, 'close'):
    conn.close()

print("\n✓ Base de dados sincronizada com sucesso!")