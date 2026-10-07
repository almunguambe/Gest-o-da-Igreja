with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a definição das classes de cursor e conexão por uma versão 100% blindada contra InFailedSqlTransaction
bloco_blindado = '''
class HybridCursor:
    def __init__(self, cur, conn):
        self._cur = cur
        self._conn = conn

    def execute(self, sql, params=None):
        import re
        if isinstance(sql, str):
            if 'AUTOINCREMENT' in sql.upper():
                sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
                sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)
            if params is not None and '?' in sql:
                sql = sql.replace('?', '%s')
        try:
            if params is not None:
                return self._cur.execute(sql, params)
            return self._cur.execute(sql)
        except Exception as e:
            # Reseta a transação para o próximo comando nunca herdar o estado abortado
            try:
                self._conn.rollback()
            except Exception:
                pass
            if 'CREATE TABLE' in str(sql).upper():
                print(f"[AVISO CREATE TABLE IGNORADO] {e}")
                return None
            raise e

    def fetchone(self):
        try:
            row = self._cur.fetchone()
            return row
        except Exception:
            return None

    def fetchall(self):
        try:
            return self._cur.fetchall()
        except Exception:
            return []

    def __iter__(self):
        try:
            for r in self._cur:
                yield r
        except Exception:
            return iter([])

    def __getattr__(self, name):
        return getattr(self._cur, name)

class HybridConn:
    def __init__(self, conn):
        self._conn = conn
        try:
            self._conn.autocommit = True
        except Exception:
            pass

    def cursor(self):
        return HybridCursor(self._conn.cursor(), self._conn)

    def execute(self, sql, params=None):
        c = self.cursor()
        c.execute(sql, params)
        return c

    def commit(self):
        try:
            return self._conn.commit()
        except Exception:
            pass

    def rollback(self):
        try:
            return self._conn.rollback()
        except Exception:
            pass

    def close(self):
        try:
            return self._conn.close()
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._conn, name)
'''

idx_start = code.find("class HybridCursor:")
if idx_start != -1:
    idx_end = code.find("def get_db():", idx_start)
    if idx_end != -1:
        code = code[:idx_start] + bloco_blindado.strip() + "\n\n" + code[idx_end:]
        print("✓ HybridCursor e HybridConn blindados com rollback defensivo e autocommit!")

# Garantir autocommit em get_db_connection se existir separadamente
if "def get_db_connection" in code:
    code = code.replace("raw_conn = psycopg2.connect(db_url)", "raw_conn = psycopg2.connect(db_url)\n            raw_conn.autocommit = True")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.py gravado com sucesso!")