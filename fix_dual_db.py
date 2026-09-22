with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Injetar imports no topo
cabecalho = '''import os
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None
'''

if "import psycopg2" not in conteudo:
    conteudo = cabecalho + "\n" + conteudo

# 2. Configurar a função get_db_connection
funcao_conexao = '''
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

if "def get_db_connection():" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if l.startswith("def get_db_connection():"):
            pulando = True
            novas.append(funcao_conexao)
        elif pulando and (l.startswith("def ") or l.startswith("@app.")):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)
    conteudo = "\n".join(novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py configurado para alternar automaticamente entre local e Render PostgreSQL!")