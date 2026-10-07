with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Garantir autocommit na conexão PostgreSQL do HybridConn / get_db
trecho_antigo_raw = "raw_conn = psycopg2.connect(db_url)"
trecho_novo_raw = """raw_conn = psycopg2.connect(db_url)
            raw_conn.autocommit = True"""

if trecho_antigo_raw in code and "raw_conn.autocommit = True" not in code:
    code = code.replace(trecho_antigo_raw, trecho_novo_raw)
    print("✓ Autocommit ativado no PostgreSQL!")

# 2. Em HybridCursor, se der erro em CREATE TABLE, ignorar para nao quebrar o dashboard
trecho_cur_exec = "return self._cur.execute(sql)"
trecho_cur_blindado = """try:
            return self._cur.execute(sql)
        except Exception as e:
            if 'CREATE TABLE' in str(sql).upper():
                print(f"[AVISO IGNORADO CREATE TABLE] {e}")
                return None
            raise e"""

if trecho_cur_exec in code and "[AVISO IGNORADO CREATE TABLE]" not in code:
    code = code.replace(trecho_cur_exec, trecho_cur_blindado, 1)
    print("✓ Tratamento de CREATE TABLE blindado!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)