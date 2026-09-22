with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garantir importação de psycopg2 e os
cabecalho = '''import os
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
'''

if "import psycopg2" not in conteudo:
    conteudo = cabecalho + "\n" + conteudo

# 2. Configurar a função get_db_connection para priorizar o PostgreSQL do Render
funcao_conexao = '''
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Garante persistência total via PostgreSQL nativo do Render ou fallback local SQLite"""
    if DATABASE_URL and psycopg2:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
'''

# Substitui get_db_connection existente
if "def get_db_connection():" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if l.startswith("def get_db_connection():"):
            pulando = True
            novas.append(funcao_conexao)
        elif pulando and (l.startswith("def ") or l.startswith("init_db(")):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)
    conteudo = "\n".join(novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py configurado para persistência permanente no PostgreSQL!")