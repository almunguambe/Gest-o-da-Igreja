with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

bloco_compat_cursor = '''
import os

class HybridRow(dict):
    """Permite acesso tanto por chave row['coluna'] quanto por indice row[0]"""
    def __init__(self, cursor, row_values):
        super().__init__()
        self._values = list(row_values)
        for idx, col in enumerate(cursor.description):
            self[col.name] = row_values[idx]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._values[item]
        return super().__getitem__(item)

class HybridCursor:
    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        # Converte ? para %s se for PostgreSQL
        if params is not None and '?' in sql:
            sql = sql.replace('?', '%s')
        if params:
            return self._cur.execute(sql, params)
        return self._cur.execute(sql)

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        return HybridRow(self._cur, row)

    def fetchall(self):
        rows = self._cur.fetchall()
        return [HybridRow(self._cur, r) for r in rows]

    def __iter__(self):
        for r in self.fetchall():
            yield r

    def __getattr__(self, name):
        return getattr(self._cur, name)

class HybridConn:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return HybridCursor(self._conn.cursor())

    def execute(self, sql, params=None):
        c = self.cursor()
        c.execute(sql, params)
        return c

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)

def get_db():
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if db_url:
        try:
            import psycopg2
            raw_conn = psycopg2.connect(db_url)
            return HybridConn(raw_conn)
        except Exception as e:
            print(f"[ERRO POSTGRES get_db] {e}")

    import sqlite3
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn
'''

idx_get = code.find("def get_db():")
if idx_get != -1:
    idx_fim = code.find("def get_db_connection", idx_get)
    if idx_fim == -1:
        idx_fim = code.find("@app.", idx_get)
    if idx_fim != -1:
        code = code[:idx_get] + bloco_compat_cursor.strip() + "\n\n" + code[idx_fim:]
        print("✓ Conexão Híbrida implementada com sucesso!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)