with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a inserção do censo para usar as colunas compatíveis
codigo_censo_novo = """
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
"""

# Se a rota já existia, ajustamos para a versão nova
import re
if "@app.route('/censo'" in code:
    code = re.sub(r"@app\.route\('/censo'[\s\S]*?return render_template\('censo_form\.html', msg_erro=msg_erro\)", codigo_censo_novo.strip(), code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota /censo atualizada com sucesso no app.py!")
else:
    print("Atenção: rota não localizada para substituição direta.")