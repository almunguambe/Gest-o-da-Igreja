# -*- coding: utf-8 -*-
with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Localizar trecho de coleta de dúvidas injetado com erro de indentação
linhas_corrigidas = []
for i, linha in enumerate(linhas):
    # Se uma linha isolada tiver 12 ou 8 espaços indevidos fora de bloco de função/try
    if "duvidas_lista = []" in linha or "candidatos_discipulado = []" in linha:
        # Alinhar com 4 ou 8 espaços padrão dependendo do escopo
        indent = len(linha) - len(linha.lstrip())
        if indent > 8:
            linha = " " * 8 + linha.lstrip()
    linhas_corrigidas.append(linha)

with open('app.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Localizar o início da rota defeituosa /censo
indice_inicio = None
for idx, linha in enumerate(linhas):
    if "@app.route('/censo'" in linha or '@app.route("/censo"' in linha:
        indice_inicio = idx
        break

if indice_inicio is not None:
    # Mantém todo o código anterior intacto
    codigo_base = "".join(linhas[:indice_inicio]).rstrip()
    
    # Bloco perfeitamente alinhado sem indentação extra
    bloco_censo_corrigido = """

# =======================================================
# MÓDULO DE CENSO E AUTO-RECENSEAMENTO (ALINHADO)
# =======================================================
@app.route('/censo', methods=['GET', 'POST'])
def censo_publico():
    msg_erro = None
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        data_nascimento = request.form.get('data_nascimento')
        genero = request.form.get('genero')
        estado_civil = request.form.get('estado_civil')
        telefone = (request.form.get('telefone') or '').strip()
        bairro = request.form.get('bairro')
        endereco = request.form.get('endereco') or request.form.get('bairro')
        naturalidade = request.form.get('naturalidade')
        filiacao = request.form.get('filiacao')
        tipo_doc = request.form.get('tipo_doc')
        num_doc = request.form.get('num_doc')
        segmento = request.form.get('segmento')
        ano_conversao = request.form.get('ano_conversao')
        batizado = request.form.get('batizado', 'Não')
        cargo = request.form.get('cargo', 'Membro em Comunhão')
        departamento = request.form.get('departamento', 'Geral')
        
        recenseador = session.get('usuario', 'Auto-recenseamento (WhatsApp)')
        
        if not nome or not telefone:
            msg_erro = "Por favor, preencha o Nome Completo e o Contacto telefónico."
            return render_template('censo_form.html', msg_erro=msg_erro)
            
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

        try:
            conn = get_db()
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            status_inicial = 'Ativo' if session.get('usuario') else 'Pendente de Validação'
            
            sql = f'''
                INSERT INTO membros (
                    nome, data_nascimento, genero, estado_civil, telefone,
                    bairro, endereco, naturalidade, filiacao, tipo_doc, num_doc,
                    segmento, ano_conversao, batizado, cargo, departamento,
                    status, foto_path, professor_nome
                ) VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})
            '''
            cur.execute(sql, (
                nome, data_nascimento, genero, estado_civil, telefone,
                bairro, endereco, naturalidade, filiacao, tipo_doc, num_doc,
                segmento, ano_conversao, batizado, cargo, departamento,
                status_inicial, foto_path, recenseador
            ))
            conn.commit()
            if hasattr(conn, 'close'):
                conn.close()
                
            return render_template('censo_sucesso.html', nome=nome, status=status_inicial)
        except Exception as e:
            msg_erro = f"Erro ao registar a ficha: {e}"

    return render_template('censo_form.html', msg_erro=msg_erro)


@app.route('/admin/censo/homologar')
def painel_homologacao_censo():
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    
    cur.execute(f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, data_cadastro FROM membros WHERE status = {param} ORDER BY id DESC", ('Pendente de Validação',))
    pendentes = cur.fetchall()
    if hasattr(conn, 'close'):
        conn.close()
        
    return render_template('censo_homologar.html', pendentes=pendentes)


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
        f.write(codigo_base + bloco_censo_corrigido)
    print("✓ app.py reescrito e alinhado com sucesso!")
else:
    print("A rota /censo não foi encontrada no ficheiro.")