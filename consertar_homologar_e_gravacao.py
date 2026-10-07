with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir painel_homologacao_censo por uma consulta adaptativa
codigo_homologar_seguro = """
@app.route('/admin/censo/homologar')
def painel_homologacao_censo():
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    param = "%s" if is_pg else "?"
    
    usuario_nivel = session.get('nivel', '') or session.get('cargo', '')
    usuario_igreja = session.get('igreja', '')
    is_sede = usuario_nivel in ['Superadmin', 'Pastor Presidente', 'Administrador'] or not usuario_igreja
    filtro_igreja = request.args.get('igreja_filtro', '')
    
    lista_igrejas = ['IEAD Chicuque']
    try:
        cur.execute("SELECT nome FROM igrejas ORDER BY nome ASC")
        rows = cur.fetchall()
        if rows:
            lista_igrejas = [r[0] for r in rows if r[0]]
            if 'IEAD Chicuque' not in lista_igrejas:
                lista_igrejas.insert(0, 'IEAD Chicuque')
    except Exception:
        if is_pg:
            try:
                conn.rollback()
            except Exception:
                pass
    
    # 1. Garantir que as colunas essenciais existem antes de consultar
    colunas_essenciais = [
        ("status", "VARCHAR(50) DEFAULT 'Ativo'"),
        ("igreja", "VARCHAR(150) DEFAULT 'IEAD Chicuque'"),
        ("telefone", "VARCHAR(50)"),
        ("bairro", "VARCHAR(100)"),
        ("batizado", "VARCHAR(20) DEFAULT 'Não'"),
        ("departamento", "VARCHAR(100) DEFAULT 'Geral'"),
        ("foto_path", "VARCHAR(255)")
    ]
    for c_nome, c_tipo in colunas_essenciais:
        try:
            if is_pg:
                cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {c_nome} {c_tipo};")
            else:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {c_nome} {c_tipo};")
            conn.commit()
        except Exception:
            if is_pg:
                try:
                    conn.rollback()
                except Exception:
                    pass

    # 2. Fazer SELECT seguro com colunas garantidas
    try:
        if is_sede:
            if filtro_igreja and filtro_igreja != 'Todas':
                cur.execute(f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, igreja, status FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC", ('Pendente de Validação', filtro_igreja))
            else:
                cur.execute(f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, igreja, status FROM membros WHERE status = {param} ORDER BY id DESC", ('Pendente de Validação',))
        else:
            cur.execute(f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, igreja, status FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC", ('Pendente de Validação', usuario_igreja))
        linhas = cur.fetchall()
    except Exception as e:
        if is_pg:
            try:
                conn.rollback()
            except Exception:
                pass
        linhas = []

    # Mapear para o formato esperado pelo template
    pendentes = []
    for r in linhas:
        # id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, igreja, data_cadastro
        pendentes.append((
            r[0],
            r[1],
            r[2] if len(r) > 2 else '',
            r[3] if len(r) > 3 else '',
            r[4] if len(r) > 4 else 'Não',
            r[5] if len(r) > 5 else 'Geral',
            r[6] if len(r) > 6 else None,
            'Auto-recenseamento',
            r[7] if len(r) > 7 else 'IEAD Chicuque',
            'Recente'
        ))
        
    if hasattr(conn, 'close'):
        conn.close()
        
    return render_template(
        'censo_homologar.html', 
        pendentes=pendentes, 
        is_sede=is_sede, 
        igrejas=lista_igrejas, 
        igreja_atual=filtro_igreja or ('Todas' if is_sede else usuario_igreja),
        usuario_igreja=usuario_igreja
    )
"""

import re
padrao = r"@app\.route\('/admin/censo/homologar'\)[\s\S]*?return render_template\('censo_homologar\.html'[\s\S]*?\)"
if re.search(padrao, code):
    code = re.sub(padrao, codigo_homologar_seguro.strip(), code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota homologar blindada com auto-recuperação!")
else:
    print("Aviso: Rota não encontrada para substituição direta.")