with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

rota_teste = """
@app.route('/debug-db')
def debug_db():
    import os
    db_url = os.environ.get('DATABASE_URL', '')
    tipo_db = 'PostgreSQL (Supabase)' if ('postgresql' in db_url or 'postgres' in db_url) else 'SQLite Local'
    
    status_conexao = "Não testado"
    detalhes_erro = None
    total_membros = -1
    
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur.execute("SELECT COUNT(*) FROM membros;")
        row = cur.fetchone()
        total_membros = row[0] if row else 0
        status_conexao = "Conexão bem sucedida!"
        if hasattr(conn, 'close'):
            conn.close()
    except Exception as e:
        status_conexao = "Falha na conexão"
        detalhes_erro = str(e)
        
    return {
        "banco_detectado": tipo_db,
        "database_url_configurada": bool(db_url),
        "status_conexao": status_conexao,
        "total_membros_registados": total_membros,
        "erro": detalhes_erro
    }
"""

if '/debug-db' not in code:
    code = code.replace("if __name__ == '__main__':", rota_teste + "\n\nif __name__ == '__main__':")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota de diagnóstico /debug-db adicionada!")
else:
    print("Rota /debug-db já existe.")