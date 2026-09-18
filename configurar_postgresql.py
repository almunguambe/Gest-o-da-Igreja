import os

with open("app.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Substituir importações e conexão para suportar PostgreSQL
cabecalho_antigo = """import sqlite3
from datetime import datetime"""

cabecalho_novo = """import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime"""

codigo = codigo.replace(cabecalho_antigo, cabecalho_novo)

# Substituir a função get_db e init_db para alternar dinamicamente
bloco_db_antigo = """DB_NAME = "gestao_chicuque.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()"""

bloco_db_novo = """DB_NAME = "gestao_chicuque.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE_URL = os.environ.get("DATABASE_URL")

# Wrapper unificado para compatibilidade de consultas SQL
class DBWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return self.conn.cursor()

    def execute(self, sql, params=()):
        if self.is_pg:
            # PostgreSQL usa %s em vez de ?
            sql_pg = sql.replace('?', '%s')
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(sql_pg, params)
            return cur
        else:
            return self.conn.execute(sql, params)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db():
    if DATABASE_URL:
        # Corrigir prefixo postgres:// antigo se necessário
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url)
        return DBWrapper(conn, is_pg=True)
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return DBWrapper(conn, is_pg=False)

def init_db():
    conn = get_db()
    c = conn.cursor()"""

codigo = codigo.replace(bloco_db_antigo, bloco_db_novo)

# Substituir tipos incompatíveis nas instruções DDL para PostgreSQL
codigo = codigo.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY" if False else "INTEGER PRIMARY KEY AUTOINCREMENT")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✓ app.py configurado com suporte para PostgreSQL!")