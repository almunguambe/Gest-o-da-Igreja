with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substituir a conexão anterior pelo driver libsql_client com fallback para sqlite3
trecho_busca = 'TURSO_URL = os.environ.get("TURSO_DATABASE_URL"'

# Procurar onde começa a lógica do Turso
if trecho_busca in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    
    bloco_novo = '''TURSO_URL = os.environ.get("TURSO_DATABASE_URL", "libsql://iead-chicuque-db-almunguambe.aws-us-east-1.turso.io")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODk4MjgxNTAsImlkIjoiMDFhMGJhMTEtNTMwMS03NjVkLTliYmMtZjFiNDY1NmZmNGVjIiwia2lkIjoiUWx4ajBQTlRubjExcXVoRWpldmVmZG11Vko3T3ZsbDVwemlNUEdic2xudyIsInJpZCI6IjBmZDA1YTY4LTY0YjctNGE2Zi1hZGQxLWU2NjgzNmE5ODNmZCJ9.3ccLSnWMbwUEiWjzItQ-cHvLjyRTmHLYINWktZVyirs22ckyD6Ml2pEf6H-wGZDIN18CXYi73jy0xEVNOLNmAg")

def get_db():
    try:
        import libsql_client
        conn = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)
        # Adaptador para compatibilidade com a sintaxe do SQLite existente
        class LibSqlWrapper:
            def __init__(self, client):
                self.client = client
            def cursor(self):
                return self
            def execute(self, query, params=None):
                if params:
                    res = self.client.execute(query, list(params))
                else:
                    res = self.client.execute(query)
                self._res = res
                self._rows = res.rows
                self._idx = 0
                return self
            def executemany(self, query, seq_params):
                for p in seq_params:
                    self.execute(query, p)
                return self
            def fetchone(self):
                if hasattr(self, '_rows') and self._idx < len(self._rows):
                    row = self._rows[self._idx]
                    self._idx += 1
                    return row
                return None
            def fetchall(self):
                if hasattr(self, '_rows'):
                    return self._rows
                return []
            def commit(self):
                pass
            def close(self):
                try:
                    self.client.close()
                except:
                    pass
        return LibSqlWrapper(conn)
    except Exception as err:
        print(f"Aviso ao ligar Turso, usando sqlite local: {err}")
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn'''

    for l in linhas:
        if 'TURSO_URL = os.environ.get("TURSO_DATABASE_URL"' in l:
            pulando = True
            novas.append(bloco_novo)
        elif pulando and l.startswith("def init_db():"):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(novas))
    print("✓ app.py ajustado com libsql-client estável!")
else:
    print("Aviso: Trecho do Turso não encontrado diretamente. Verificando estrutura...")