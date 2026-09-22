with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

antigo_db = '''def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn'''

novo_db = '''TURSO_URL = os.environ.get("TURSO_DATABASE_URL", "libsql://iead-chicuque-db-almunguambe.aws-us-east-1.turso.io")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODk4MjgxNTAsImlkIjoiMDFhMGJhMTEtNTMwMS03NjVkLTliYmMtZjFiNDY1NmZmNGVjIiwia2lkIjoiUWx4ajBQTlRubjExcXVoRWpldmVmZG11Vko3T3ZsbDVwemlNUEdic2xudyIsInJpZCI6IjBmZDA1YTY4LTY0YjctNGE2Zi1hZGQxLWU2NjgzNmE5ODNmZCJ9.3ccLSnWMbwUEiWjzItQ-cHvLjyRTmHLYINWktZVyirs22ckyD6Ml2pEf6H-wGZDIN18CXYi73jy0xEVNOLNmAg")

def get_db():
    try:
        import libsql_experimental as libsql
        conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as err:
        print(f"Aviso conexao Turso, usando sqlite local: {err}")
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn'''

if "def get_db():" in conteudo:
    # Substituir get_db
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if "def get_db():" in l:
            pulando = True
            novas.append(novo_db)
        elif pulando and (l.startswith("def init_db():") or l.startswith("def ")):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)
            
    conteudo_final = "\n".join(novas)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(conteudo_final)
    print("✓ app.py configurado para conectar ao Turso Cloud!")
else:
    print("! Nao foi possivel localizar get_db()")