with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

nova_rota_homologar = """
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
    
    # Filtro opcional selecionado na URL pelo Admin da Sede
    filtro_igreja = request.args.get('igreja_filtro', '')
    
    # Buscar lista de todas as congregações cadastradas
    lista_igrejas = ['IEAD Chicuque']
    try:
        cur.execute("SELECT nome FROM igrejas ORDER BY nome ASC")
        rows = cur.fetchall()
        if rows:
            lista_igrejas = [r[0] for r in rows if r[0]]
            if 'IEAD Chicuque' not in lista_igrejas:
                lista_igrejas.insert(0, 'IEAD Chicuque')
    except Exception:
        pass
    
    # Construir consulta de membros pendentes conforme permissão
    colunas_sql = "id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, igreja, data_cadastro"
    
    if is_sede:
        if filtro_igreja and filtro_igreja != 'Todas':
            query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC"
            cur.execute(query, ('Pendente de Validação', filtro_igreja))
        else:
            query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} ORDER BY id DESC"
            cur.execute(query, ('Pendente de Validação',))
    else:
        # Secretário local: restrito à sua congregação
        query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC"
        cur.execute(query, ('Pendente de Validação', usuario_igreja))
        
    pendentes = cur.fetchall()
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
    code = re.sub(padrao, nova_rota_homologar.strip(), code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota de homologação multi-congregação aplicada com sucesso!")
else:
    print("Aviso: Rota anterior não localizada para substituição direta.")