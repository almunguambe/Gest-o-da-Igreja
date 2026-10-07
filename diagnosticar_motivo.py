with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

rota_raio_x = """
@app.route('/debug-check-env')
def debug_check_env():
    import os
    import sys
    
    # 1. Testar import do psycopg2
    erro_import = None
    tem_psycopg2 = False
    try:
        import psycopg2
        tem_psycopg2 = True
    except Exception as e:
        erro_import = str(e)

    # 2. Varrer todas as variáveis de ambiente em busca de URL do banco
    url_padrao = os.environ.get("DATABASE_URL")
    url_limpa = url_padrao[:15] + "..." if url_padrao else None
    
    todas_chaves_db = [k for k in os.environ.keys() if 'DATA' in k or 'POSTGRES' in k or 'DB' in k or 'SUPA' in k]

    return {
        "psycopg2_instalado": tem_psycopg2,
        "erro_import_psycopg2": erro_import,
        "DATABASE_URL_encontrada": bool(url_padrao),
        "prefixo_url": url_limpa,
        "variaveis_relacionadas": todas_chaves_db,
        "python_version": sys.version
    }
"""

if '/debug-check-env' not in code:
    code += "\n" + rota_raio_x
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /debug-check-env adicionada com sucesso!")
else:
    print("Rota já estava presente.")