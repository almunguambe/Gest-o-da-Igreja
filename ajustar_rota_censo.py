with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a verificação de colunas da rota /censo por uma abordagem compatível e robusta
trecho_antigo = """        try:
            if is_pg:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
                cols_db = [r[0].lower() for r in cur.fetchall()]
            else:
                cur.execute("PRAGMA table_info(membros);")
                cols_db = [r[1].lower() for r in cur.fetchall()]"""

trecho_novo = """        try:
            # Detectar banco real em execução
            is_postgres_real = hasattr(conn, 'cursor_factory') or 'psycopg' in str(type(conn)).lower() or bool(DATABASE_URL and psycopg2)
            if is_postgres_real:
                try:
                    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
                    cols_db = [r[0].lower() for r in cur.fetchall()]
                except Exception:
                    # Fallback com colunas padrão da tabela membros caso haja erro de permissão no schema
                    cols_db = ['nome', 'telefone', 'igreja', 'data_nascimento', 'genero', 'estado_civil', 'bairro', 'endereco', 'naturalidade', 'filiacao', 'tipo_doc', 'num_doc', 'segmento', 'ano_conversao', 'batizado', 'cargo', 'departamento', 'status', 'foto_path', 'professor_nome']
            else:
                cur.execute("PRAGMA table_info(membros);")
                cols_db = [r[1].lower() for r in cur.fetchall()]"""

if trecho_antigo in code:
    code = code.replace(trecho_antigo, trecho_novo, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /censo ajustada com sucesso!")
else:
    # Se houver pequenas variações de espaçamento, faz substituição por regex
    import re
    padrao = r'if is_pg:\s+cur\.execute\("SELECT column_name FROM information_schema\.columns WHERE table_name = \'membros\';"\)[\s\S]*?cols_db = \[r\[1\]\.lower\(\) for r in cur\.fetchall\(\)\]'
    if re.search(padrao, code):
        code = re.sub(padrao, trecho_novo.strip(), code, count=1)
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("✓ Rota /censo ajustada via regex!")
    else:
        print("Trecho não encontrado automaticamente para substituição.")