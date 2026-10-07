with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a linha que fixa colunas_sql por verificação dinâmica
antigo = 'colunas_sql = "id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, igreja, data_cadastro"'
novo = """
    # Verificar colunas existentes dinamicamente
    if is_pg:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
        cols_ativas = [r[0].lower() for r in cur.fetchall()]
    else:
        cur.execute("PRAGMA table_info(membros);")
        cols_ativas = [r[1].lower() for r in cur.fetchall()]

    col_batizado = "batizado" if "batizado" in cols_ativas else "'Não' as batizado"
    col_igreja = "igreja" if "igreja" in cols_ativas else "'IEAD Chicuque' as igreja"
    col_status = "status" if "status" in cols_ativas else "'Ativo' as status"
    col_tel = "telefone" if "telefone" in cols_ativas else "'' as telefone"
    col_bairro = "bairro" if "bairro" in cols_ativas else "'' as bairro"
    col_dep = "departamento" if "departamento" in cols_ativas else "'Geral' as departamento"
    col_foto = "foto_path" if "foto_path" in cols_ativas else "NULL as foto_path"

    colunas_sql = f"id, nome, {col_tel}, {col_bairro}, {col_batizado}, {col_dep}, {col_foto}, {col_igreja}"
"""

if antigo in code:
    code = code.replace(antigo, novo)
    # Ajustar a montagem dos pendentes para o número correto de colunas
    antigo_pendentes = "pendentes = cur.fetchall()"
    novo_pendentes = """linhas = cur.fetchall()
    pendentes = []
    for r in linhas:
        pendentes.append((
            r[0], r[1], r[2], r[3], r[4], r[5], r[6], 'Auto-recenseamento', r[7], 'Recente'
        ))"""
    if antigo_pendentes in code:
        code = code.replace(antigo_pendentes, novo_pendentes, 1)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ app.py blindado contra ausência de colunas!")
else:
    print("Linha alvo já substituída ou modificada.")