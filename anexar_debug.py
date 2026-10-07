with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

rota = """

# =====================================================================
# ROTA DE TESTE E DIAGNÓSTICO DO SUPABASE
# =====================================================================
@app.route('/debug-db')
def rota_debug_supabase():
    import os
    db_env = os.environ.get('DATABASE_URL', '')
    status_conexao = "Aguardando teste"
    erro_detalhado = None
    total_linhas = -1
    tipo = "PostgreSQL (Supabase)" if ("postgres" in db_env.lower()) else "SQLite Local"
    
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur.execute("SELECT COUNT(*) FROM membros;")
        row = cur.fetchone()
        total_linhas = row[0] if row else 0
        status_conexao = "Conexão bem sucedida!"
        if hasattr(conn, 'close'):
            conn.close()
    except Exception as e:
        status_conexao = "Falha ao conectar/consultar"
        erro_detalhado = str(e)

    return {
        "banco_detectado": tipo,
        "database_url_preenchida": bool(db_env),
        "status_conexao": status_conexao,
        "total_membros": total_linhas,
        "detalhe_erro": erro_detalhado
    }
"""

if '/debug-db' not in conteudo:
    # Insere antes do if __name__ == '__main__':
    if "if __name__ == '__main__':" in conteudo:
        conteudo = conteudo.replace("if __name__ == '__main__':", rota + "\n\nif __name__ == '__main__':")
    else:
        conteudo += rota
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Rota /debug-db inserida com sucesso!")
else:
    print("✓ Rota /debug-db já constava no app.py.")