with open('app.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Localizar o início da rota /censo
idx_censo = None
for idx, l in enumerate(linhas):
    if "@app.route('/censo'" in l or '@app.route("/censo"' in l:
        idx_censo = idx
        break

if idx_censo is not None:
    codigo_limpo = "".join(linhas[:idx_censo]).rstrip()
else:
    codigo_limpo = "".join(linhas).rstrip()

# Bloco com alinhamento rigoroso na margem esquerda (0 espaços de avanço inicial)
bloco_censo_perfeito = """

# =====================================================================
# ROTA OFICIAL DO CENSO MULTI-CONGREGAÇÃO (AUTO-RECUPERÁVEL)
# =====================================================================
@app.route('/censo', methods=['GET', 'POST'])
def censo_publico():
    msg_erro = None
    igreja_param = request.args.get('igreja', 'IEAD Chicuque')
    
    colunas_obrigatorias = [
        ("igreja", "TEXT"),
        ("batizado", "TEXT"),
        ("data_batismo", "TEXT"),
        ("endereco", "TEXT"),
        ("bairro", "TEXT"),
        ("naturalidade", "TEXT"),
        ("filiacao", "TEXT"),
        ("tipo_doc", "TEXT"),
        ("num_doc", "TEXT"),
        ("segmento", "TEXT"),
        ("ano_conversao", "TEXT"),
        ("cargo", "TEXT"),
        ("departamento", "TEXT"),
        ("status", "TEXT"),
        ("foto_path", "TEXT"),
        ("professor_nome", "TEXT")
    ]
    
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    
    for col, tipo in colunas_obrigatorias:
        try:
            if is_pg:
                cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
            else:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            conn.commit()
        except Exception:
            if is_pg:
                conn.rollback()

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

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        telefone = (request.form.get('telefone') or '').strip()
        igreja_escolhida = request.form.get('igreja') or igreja_param
        
        if not nome or not telefone:
            msg_erro = "Por favor, preencha o Nome Completo e o Contacto telefónico."
            if hasattr(conn, 'close'):
                conn.close()
            return render_template('censo_form.html', msg_erro=msg_erro, igrejas=lista_igrejas, igreja_selecionada=igreja_param)
            
        foto_path = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                nome_foto = f"membro_{int(time.time())}.{ext}"
                caminho_salvar = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), nome_foto)
                os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
                file.save(caminho_salvar)
                foto_path = f"/static/uploads/{nome_foto}"

        campos = {
            'nome': nome,
            'telefone': telefone,
            'igreja': igreja_escolhida,
            'data_nascimento': request.form.get('data_nascimento'),
            'genero': request.form.get('genero'),
            'estado_civil': request.form.get('estado_civil'),
            'bairro': request.form.get('bairro'),
            'endereco': request.form.get('endereco') or request.form.get('bairro'),
            'naturalidade': request.form.get('naturalidade'),
            'filiacao': request.form.get('filiacao'),
            'tipo_doc': request.form.get('tipo_doc'),
            'num_doc': request.form.get('num_doc'),
            'segmento': request.form.get('segmento'),
            'ano_conversao': request.form.get('ano_conversao'),
            'batizado': request.form.get('batizado', 'Não'),
            'cargo': request.form.get('cargo', 'Membro em Comunhão'),
            'departamento': request.form.get('departamento', 'Geral'),
            'status': 'Pendente de Validação',
            'foto_path': foto_path,
            'professor_nome': session.get('usuario', 'Auto-recenseamento')
        }

        try:
            if is_pg:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
                cols_db = [r[0].lower() for r in cur.fetchall()]
            else:
                cur.execute("PRAGMA table_info(membros);")
                cols_db = [r[1].lower() for r in cur.fetchall()]
                
            cols_inserir = [k for k in campos.keys() if k.lower() in cols_db]
            vals_inserir = [campos[k] for k in cols_inserir]
            
            param = "%s" if is_pg else "?"
            sql = f"INSERT INTO membros ({', '.join(cols_inserir)}) VALUES ({', '.join([param]*len(cols_inserir))})"
            cur.execute(sql, tuple(vals_inserir))
            conn.commit()
            if hasattr(conn, 'close'):
                conn.close()
            return render_template('censo_sucesso.html', nome=nome, status='Pendente de Validação', igreja=igreja_escolhida)
        except Exception as e:
            msg_erro = f"Erro ao registar a ficha: {e}"

    if hasattr(conn, 'close'):
        conn.close()
    return render_template('censo_form.html', msg_erro=msg_erro, igrejas=lista_igrejas, igreja_selecionada=igreja_param)


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
        pass
    
    colunas_sql = "id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, igreja, data_cadastro"
    
    if is_sede:
        if filtro_igreja and filtro_igreja != 'Todas':
            cur.execute(f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC", ('Pendente de Validação', filtro_igreja))
        else:
            cur.execute(f"SELECT {colunas_sql} FROM membros WHERE status = {param} ORDER BY id DESC", ('Pendente de Validação',))
    else:
        cur.execute(f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC", ('Pendente de Validação', usuario_igreja))
        
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


@app.route('/admin/censo/aprovar/<int:membro_id>', methods=['POST'])
def aprovar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"UPDATE membros SET status = {param} WHERE id = {param}", ('Ativo', membro_id))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')


@app.route('/admin/censo/descartar/<int:membro_id>', methods=['POST'])
def descartar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"DELETE FROM membros WHERE id = {param}", (membro_id,))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(codigo_limpo + bloco_censo_perfeito)

print("✓ app.py reescrito e alinhado com sucesso!")