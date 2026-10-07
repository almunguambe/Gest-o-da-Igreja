with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Garantir que DATABASE_URL é lida diretamente do ambiente
bloco_get_db_novo = """
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db():
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url:
        try:
            import psycopg2
            from psycopg2.extras import DictCursor
            conn = psycopg2.connect(db_url)
            return conn
        except Exception as e:
            print(f"[ERRO POSTGRES] Falha ao conectar: {e}")

    # Fallback SQLite apenas se não houver DATABASE_URL
    import sqlite3
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection():
    return get_db()
"""

# 2. Vamos procurar onde está get_db() no código e substituir com segurança
idx_get_db = code.find("def get_db():")
if idx_get_db != -1:
    inicio = code.rfind("DATABASE_URL =", 0, idx_get_db)
    if inicio == -1:
        inicio = idx_get_db
    # Encontra o fim da função get_db ou get_db_connection
    fim = code.find("app.secret_key", idx_get_db)
    if fim != -1:
        code = code[:inicio] + bloco_get_db_novo.strip() + "\n\n" + code[fim:]
        print("✓ get_db atualizado com sucesso!")

# 3. Na rota censo, garantir que o placeholder e a verificação sejam universais
# Se for sqlite usa ?, se for postgres usa %s
trecho_antigo_insert = """            param = "%s" if is_pg else "?"
            sql = f"INSERT INTO membros ({', '.join(cols_inserir)}) VALUES ({', '.join([param]*len(cols_inserir))})"
            cur.execute(sql, tuple(vals_inserir))"""

trecho_novo_insert = """            # Detectar dinamicamente se o conn é postgres ou sqlite
            is_real_pg = 'psycopg' in str(type(conn)).lower()
            param = "%s" if is_real_pg else "?"
            sql = f"INSERT INTO membros ({', '.join(cols_inserir)}) VALUES ({', '.join([param]*len(cols_inserir))})"
            cur.execute(sql, tuple(vals_inserir))"""

if trecho_antigo_insert in code:
    code = code.replace(trecho_antigo_insert, trecho_novo_insert)
    print("✓ Lógica de placeholder ajustada com sucesso!")
else:
    # Ajuste alternativo se o trecho tiver variações
    import re
    code = re.sub(
        r'param = "%s" if .*? else "\?"\s+sql = f"INSERT INTO membros',
        'is_real_pg = \'psycopg\' in str(type(conn)).lower()\n            param = "%s" if is_real_pg else "?"\n            sql = f"INSERT INTO membros',
        code
    )
    print("✓ Placeholder ajustado via padrão!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Ficheiro app.py gravado!")