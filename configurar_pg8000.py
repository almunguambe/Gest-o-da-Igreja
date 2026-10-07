with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

novo_bloco = '''import os
import sqlite3
import urllib.parse as up

# Suporte nativo a PostgreSQL via pg8000 (compatível com Python 3.14+)
has_postgres = False
try:
    import pg8000.dbapi as pg_driver
    has_postgres = True
except Exception:
    try:
        import psycopg2 as pg_driver
        has_postgres = True
    except Exception:
        pg_driver = None

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db():
    global DATABASE_URL, has_postgres, pg_driver
    if DATABASE_URL:
        # Tentativa 1: pg8000 dbapi com decomposição de URL
        try:
            import pg8000.dbapi
            u = up.urlparse(DATABASE_URL)
            conn = pg8000.dbapi.connect(
                user=u.username,
                password=u.password,
                host=u.hostname,
                port=u.port or 5432,
                database=u.path.lstrip('/')
            )
            return conn
        except Exception as e_pg8000:
            print(f"[ALERTA BD] Erro ao conectar via pg8000: {e_pg8000}")

        # Tentativa 2: psycopg2 caso esteja disponível
        try:
            import psycopg2
            return psycopg2.connect(DATABASE_URL)
        except Exception:
            pass

    # Fallback SQLite local
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection():
    return get_db()
'''

# Localizar e substituir o bloco de conexão antigo
idx_db = code.find("def get_db():")
if idx_db != -1:
    inicio = code.rfind("DATABASE_URL =", 0, idx_db)
    fim = code.find("app.secret_key", idx_db)
    if inicio != -1 and fim != -1:
        code = code[:inicio] + novo_bloco + "\n\n" + code[fim:]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("✓ Conexão atualizada com pg8000!")
    else:
        print("Não foi possível delimitar o trecho exato.")
else:
    print("def get_db() não encontrado.")