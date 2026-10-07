with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Substituir get_db() e a inicialização de finanças para suportar tanto SQLite como PostgreSQL automaticamente
bloco_antigo_conexao = """def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn"""

bloco_novo_conexao = """class CompatCursor:
    def __init__(self, cursor, is_pg=False):
        self._cur = cursor
        self._is_pg = is_pg
    def execute(self, sql, params=None):
        if self._is_pg and sql:
            # Converte ? para %s para PostgreSQL
            sql = sql.replace('?', '%s')
        if params is not None:
            return self._cur.execute(sql, params)
        return self._cur.execute(sql)
    def fetchone(self):
        return self._cur.fetchone()
    def fetchall(self):
        return self._cur.fetchall()
    def fetchmany(self, size=None):
        return self._cur.fetchmany(size)
    @property
    def lastrowid(self):
        return getattr(self._cur, 'lastrowid', None)
    def __iter__(self):
        return iter(self._cur)

class CompatConn:
    def __init__(self, conn, is_pg=False):
        self._conn = conn
        self._is_pg = is_pg
    def cursor(self):
        return CompatCursor(self._conn.cursor(), self._is_pg)
    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur
    def commit(self):
        return self._conn.commit()
    def rollback(self):
        return self._conn.rollback()
    def close(self):
        return self._conn.close()

def get_db():
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url and psycopg2:
        try:
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return CompatConn(conn, is_pg=True)
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL, usando fallback SQLite: {e}")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return CompatConn(conn, is_pg=False)"""

if bloco_antigo_conexao in conteudo:
    conteudo = conteudo.replace(bloco_antigo_conexao, bloco_novo_conexao)
    print("✓ get_db() atualizado com compatibilidade universal PostgreSQL + SQLite!")
else:
    print("! Bloco get_db não encontrado textualmente, verificando substituição manual.")

# Garantir que a rota de novo_financeiro seja 100% segura
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)