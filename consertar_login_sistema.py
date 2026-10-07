with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Configurar get_db para usar DictCursor no PostgreSQL
bloco_get_db_dict = '''
def get_db():
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if db_url:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            # cursor_factory=RealDictCursor permite aceder a r['campo'] exatamente como no SQLite
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            return conn
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
        code = code[:idx_get] + bloco_get_db_dict.strip() + "\n\n" + code[idx_fim:]
        print("✓ get_db() atualizado com RealDictCursor para compatibilidade total!")

# 2. Assegurar criacao da tabela usuarios no init_db para PostgreSQL
trecho_init_antigo = 'CREATE TABLE IF NOT EXISTS igrejas ('
trecho_usuarios_pg = '''CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    nivel TEXT DEFAULT 'admin'
                );
                CREATE TABLE IF NOT EXISTS igrejas ('''

if trecho_init_antigo in code and 'CREATE TABLE IF NOT EXISTS usuarios' not in code:
    code = code.replace(trecho_init_antigo, trecho_usuarios_pg, 1)
    print("✓ Tabela de usuarios adicionada ao init_db()!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)