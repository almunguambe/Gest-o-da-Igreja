with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Substituir qualquer ocorrência estática de AUTOINCREMENT no app.py
code = code.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
code = code.replace("integer primary key autoincrement", "serial primary key")
code = code.replace("AUTOINCREMENT", "")

# 2. Localizar e substituir a implementação do HybridCursor / execute
bloco_cursor_universal = '''
class HybridCursor:
    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        import re
        if isinstance(sql, str):
            # Converte tipos e palavras exclusivas do SQLite para PostgreSQL
            if 'AUTOINCREMENT' in sql.upper():
                sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
                sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)
            if params is not None and '?' in sql:
                sql = sql.replace('?', '%s')
        if params is not None:
            return self._cur.execute(sql, params)
        return self._cur.execute(sql)

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        return row

    def fetchall(self):
        return self._cur.fetchall()

    def __iter__(self):
        for r in self._cur:
            yield r

    def __getattr__(self, name):
        return getattr(self._cur, name)
'''

idx_cur = code.find("class HybridCursor:")
if idx_cur != -1:
    idx_conn = code.find("class HybridConn:", idx_cur)
    if idx_conn != -1:
        code = code[:idx_cur] + bloco_cursor_universal.strip() + "\n\n" + code[idx_conn:]
        print("✓ HybridCursor reconstruído com sanitização universal de SQL!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.py saneado com sucesso!")