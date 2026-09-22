with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

bloco_conexao = '''
import os
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL and psycopg2:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn
'''

# Se já houver get_db_connection, removemos duplicatas quebradas e colocamos no lugar certo
if "def get_db_connection():" in conteudo:
    partes = conteudo.split("def get_db_connection():")
    # Mantém o topo e o resto
    conteudo = partes[0] + partes[1].split("\n@app.", 1)[-1]
    conteudo = "@app." + conteudo

# Adicionar no topo logo após a inicialização do Flask (app = Flask(...))
if "app = Flask(" in conteudo:
    partes = conteudo.split("app = Flask(")
    resto = partes[1].split("\n", 1)
    conteudo = partes[0] + "app = Flask(" + resto[0] + "\n" + bloco_conexao + "\n" + resto[1]
else:
    conteudo = bloco_conexao + "\n" + conteudo

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ get_db_connection posicionada corretamente antes de todas as rotas!")