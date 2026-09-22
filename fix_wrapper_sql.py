with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substituir a classe DBWrapper por uma versão blindada contra % e tuplas
trecho_antigo = """class DBWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        q = query
        if self.is_pg:
            # Converte marcadores ? para %s para PostgreSQL
            q = q.replace("?", "%s")
        try:
            if params:
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            print(f"Erro SQL ({q}): {e}")
            raise e
        return cur"""

trecho_novo = """class DBWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        q = query
        if self.is_pg:
            # Protege símbolos de % normais (como LIKE '%...' ou strftime) escapando-os como %%
            q = q.replace("%", "%%")
            # Converte marcadores ? para %s real do psycopg2
            q = q.replace("?", "%s")
            # Caso a query já tivesse %%s por engano, restaura
            q = q.replace("%%%%s", "%s")
        try:
            if params is not None:
                # Garante formato tupla ou lista aceito pelo psycopg2
                if not isinstance(params, (list, tuple)):
                    params = (params,)
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            print(f"Erro SQL ({q}): {e}")
            raise e
        return cur"""

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✓ DBWrapper atualizado com escape seguro de parâmetros!")
else:
    # Se houver variação de espaçamento, busca por linhas
    print("! Aplicando substituição flexível...")
    linhas = conteudo.splitlines()
    novas_linhas = []
    ignorar = False
    for l in linhas:
        if "class DBWrapper:" in l:
            ignorar = True
            novas_linhas.append(trecho_novo)
        elif ignorar and l.startswith("def get_db():"):
            ignorar = False
            novas_linhas.append(l)
        elif not ignorar:
            novas_linhas.append(l)
            
    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(novas_linhas))
    print("✓ DBWrapper atualizado com sucesso!")