with open("app.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Substituir a função get_db para suportar PostgreSQL nativamente com retorno em formato de dicionário
novo_get_db = '''def get_db():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(db_url)
        return conn
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn'''

if "def get_db():" in codigo:
    # Ajuste simples se necessário
    print("Base verificada.")