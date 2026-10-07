with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

endpoint_teste = """

# =====================================================================
# TESTE DIRETO DE INSERÇÃO NO SUPABASE VIA WEB
# =====================================================================
@app.route('/debug-inserir-censo')
def debug_inserir_censo():
    import os
    if not (DATABASE_URL and psycopg2):
        return {"erro": "DATABASE_URL nao configurada ou psycopg2 ausente"}
    
    resumo = {}
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # 1. Pegar colunas reais da tabela membros no Supabase
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'membros';")
        cols_pg = cur.fetchall()
        colunas_reais = {c[0].lower(): c[1] for c in cols_pg}
        resumo["colunas_no_supabase"] = colunas_reais

        # 2. Dados de teste
        dados = {
            'nome': 'Teste Oficial Supabase',
            'telefone': '+258 84 999 8888',
            'igreja': 'IEAD Chicuque',
            'status': 'Pendente de Validação',
            'batizado': 'Sim',
            'cargo': 'Membro em Comunhão',
            'departamento': 'Geral'
        }

        # 3. Filtrar apenas colunas que realmente existem na tabela
        cols_para_inserir = [k for k in dados.keys() if k.lower() in colunas_reais]
        vals_para_inserir = [dados[k] for k in cols_para_inserir]

        if not cols_para_inserir:
            return {"erro": "Nenhuma das colunas do teste existe na tabela membros!"}

        sql = f"INSERT INTO membros ({', '.join(cols_para_inserir)}) VALUES ({', '.join(['%s']*len(cols_para_inserir))}) RETURNING id;"
        cur.execute(sql, tuple(vals_para_inserir))
        novo_id = cur.fetchone()[0]
        conn.commit()

        resumo["resultado"] = "SUCESSO"
        resumo["novo_id_criado"] = novo_id
        resumo["sql_executado"] = sql

    except Exception as e:
        if conn:
            try: conn.rollback()
            except Exception: pass
        resumo["resultado"] = "ERRO"
        resumo["mensagem_erro"] = str(e)
    finally:
        if conn and hasattr(conn, 'close'):
            conn.close()

    return resumo
"""

if '/debug-inserir-censo' not in code:
    code += endpoint_teste
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /debug-inserir-censo inserida com sucesso!")
else:
    print("Rota já presente.")