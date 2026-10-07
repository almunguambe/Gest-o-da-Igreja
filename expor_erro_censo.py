with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fazer a rota /censo exibir a mensagem de erro exata na tela em vez do erro 500 genérico
trecho_busca = "def censo():"
if "def censo_publico():" in code:
    trecho_busca = "def censo_publico():"

idx = code.find(trecho_busca)
if idx != -1:
    print(f"✓ Rota encontrada: {trecho_busca}")

# Garantir que o bloco de conexão get_db entregue a conexão do psycopg2 diretamente
bloco_get_db_direto = """
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
            print(f"[ERRO POSTGRES get_db] {e}")

    import sqlite3
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn
"""

idx_get = code.find("def get_db():")
if idx_get != -1:
    idx_fim_get = code.find("def get_db_connection", idx_get)
    if idx_fim_get == -1:
        idx_fim_get = code.find("@app.route", idx_get)
    if idx_fim_get != -1:
        code = code[:idx_get] + bloco_get_db_direto.strip() + "\n\n" + code[idx_fim_get:]
        print("✓ get_db() simplificado para entregar psycopg2 direto!")

# Tratamento de erro detalhado na rota do censo
trecho_tratamento = """
@app.errorhandler(500)
def erro_interno_500(e):
    import traceback
    return f"<h3>Erro Interno (500):</h3><pre>{traceback.format_exc()}</pre>", 500
"""

if "@app.errorhandler(500)" not in code:
    code += "\n\n" + trecho_tratamento.strip()
    print("✓ Capturador de erro 500 adicionado!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)