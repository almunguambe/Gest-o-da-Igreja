with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a rota /debug-db por uma versão que testa a função get_db() e reporta o erro real
trecho_debug = """
@app.route('/debug-db')
def rota_debug_supabase():
    import os
    import sys
    db_env = os.environ.get('DATABASE_URL', '')
    
    teste_conexao_direta = None
    erro_direto = None
    try:
        import psycopg2
        c = psycopg2.connect(db_env)
        teste_conexao_direta = "Sucesso na conexão direta via psycopg2"
        c.close()
    except Exception as e:
        erro_direto = str(e)

    # Testar o que get_db() devolve
    tipo_get_db = None
    erro_get_db = None
    try:
        conn = get_db()
        tipo_get_db = str(type(conn))
        if hasattr(conn, 'close'):
            conn.close()
    except Exception as e:
        erro_get_db = str(e)

    return {
        "DATABASE_URL_configurada": bool(db_env),
        "conexao_direta_psycopg2": teste_conexao_direta,
        "erro_conexao_direta": erro_direto,
        "tipo_retornado_por_get_db": tipo_get_db,
        "erro_get_db": erro_get_db
    }
"""

# Substituir a rota antiga de debug
idx_rota = code.find("@app.route('/debug-db')")
if idx_rota != -1:
    idx_prox = code.find("@app.route", idx_rota + 10)
    if idx_prox != -1:
        code = code[:idx_rota] + trecho_debug.strip() + "\n\n" + code[idx_prox:]
    else:
        # Se for no fim do arquivo
        idx_main = code.find("if __name__", idx_rota)
        if idx_main != -1:
            code = code[:idx_rota] + trecho_debug.strip() + "\n\n" + code[idx_main:]
        else:
            code = code[:idx_rota] + trecho_debug.strip()
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /debug-db atualizada com teste aprofundado!")
else:
    code += "\n\n" + trecho_debug.strip()
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /debug-db inserida!")