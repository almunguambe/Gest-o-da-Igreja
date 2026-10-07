with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Código de conexão robusto que corrige a URL do Supabase e avisa no log
novo_bloco_db = """DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db():
    global DATABASE_URL
    if DATABASE_URL and psycopg2:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(f"[ALERTA BD] Falha ao conectar ao Supabase: {e}")
    # Fallback SQLite local
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection():
    return get_db()
"""

# Substituir a definição antiga
import re
padrao = r'DATABASE_URL = os\.environ\.get\("DATABASE_URL"\)[\s\S]*?def get_db_connection\(\):[\s\S]*?return conn'

if re.search(padrao, code):
    code = re.sub(padrao, novo_bloco_db.strip(), code, count=1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Conexão com Supabase corrigida e padronizada em app.py!")
else:
    # Se não bater exatamente pelo regex, substituir de forma direta
    antigo_trecho = 'DATABASE_URL = os.environ.get("DATABASE_URL")'
    if antigo_trecho in code:
        idx = code.find(antigo_trecho)
        idx_fim = code.find('app.secret_key', idx)
        if idx_fim != -1:
            code = code[:idx] + novo_bloco_db + "\n\n" + code[idx_fim:]
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(code)
            print("✓ Substituição por bloco direto concluída!")
        else:
            print("Não foi possível determinar o fim do bloco.")