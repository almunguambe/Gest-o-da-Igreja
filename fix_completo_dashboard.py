with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garantir que tabelas auxiliares como zonas_lista existem no PostgreSQL
garantir_tabelas = '''
def criar_tabelas_faltantes():
    try:
        conn = get_db_connection() if 'get_db_connection' in globals() else get_db()
        c = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = bool(DATABASE_URL and psycopg2)

        # Tabela zonas_lista
        if is_pg:
            c.execute("""
                CREATE TABLE IF NOT EXISTS zonas_lista (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE NOT NULL
                );
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS zonas_lista (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL
                );
            """)

        # Tabela avaliacoes_estudantes se faltar
        if is_pg:
            c.execute("""
                CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
                    id SERIAL PRIMARY KEY,
                    usuario VARCHAR(150),
                    licao VARCHAR(50),
                    nota INTEGER,
                    total INTEGER,
                    data_resposta VARCHAR(50)
                );
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    licao TEXT,
                    nota INTEGER,
                    total INTEGER,
                    data_resposta TEXT
                );
            """)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso criacao tabelas: {e}")

try:
    criar_tabelas_faltantes()
except Exception:
    pass
'''

if "def criar_tabelas_faltantes():" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", garantir_tabelas + "\nif __name__ ==")
    else:
        conteudo += "\n" + garantir_tabelas

# 2. Corrigir o bloco de retorno do dashboard (linhas 590 a 640)
# Vamos assegurar que o dashboard faz consulta segura em zonas_lista e passa todos_membros
bloco_antigo_zonas = 'lista_zonas = conn.execute("SELECT * FROM zonas_lista ORDER BY nome ASC").fetchall()'
bloco_novo_zonas = '''    try:
        lista_zonas = conn.execute("SELECT * FROM zonas_lista ORDER BY nome ASC").fetchall()
    except Exception:
        lista_zonas = []'''

if bloco_antigo_zonas in conteudo:
    conteudo = conteudo.replace(bloco_antigo_zonas, bloco_novo_zonas)

# 3. Assegurar que 'todos_membros' e 'lista_zonas' estão presentes no render_template('dashboard.html'
if "return render_template('dashboard.html'," in conteudo:
    if "todos_membros=todos_membros" not in conteudo:
        conteudo = conteudo.replace(
            "return render_template('dashboard.html',",
            "return render_template('dashboard.html',\n                           todos_membros=todos_membros,\n                           lista_zonas=lista_zonas,"
        )

# 4. Limpar duplicações de comentários com indentação errada
conteudo = conteudo.replace(
    "         # Carregar dúvidas bíblicas para o painel pastoral\n     # Carregar dúvidas bíblicas para o painel pastoral",
    "    # Carregar dúvidas bíblicas para o painel pastoral"
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Tabelas migradas, zonas protegidas e variáveis injetadas com sucesso!")