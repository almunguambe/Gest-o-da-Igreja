with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

antigo_bloco = """@app.route('/escalas/novo', methods=['POST'])
def nova_escala():
     if not is_admin() and not can_cadastro(): return redirect('/')
     conn = get_db()
     igreja_id = session.get('igreja_id', 1)
     conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes, telefone_dirigente, telefone_pregador, igreja_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (request.form['data_escala'], request.form['tipo_culto'], request.form.get('dirigente', ''),
                   request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                   request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', ''),
                   request.form.get('telefone_dirigente', ''), request.form.get('telefone_pregador', ''), igreja_id))
     conn.commit()
     conn.close()
     session['sucesso_cadastro'] = "Escala registada!"
     return redirect('/')"""

novo_bloco = """@app.route('/escalas/novo', methods=['GET', 'POST'])
def nova_escala():
     if request.method == 'GET':
         return redirect('/#aba-escalas')
         
     if not is_admin() and not can_cadastro(): 
         return redirect('/')
         
     data_escala = request.form.get('data_escala', '').strip()
     tipo_culto = request.form.get('tipo_culto', '').strip()
     
     if not data_escala or not tipo_culto:
         flash("Por favor, preencha a data e o tipo de culto da escala.", "erro")
         return redirect('/#aba-escalas')

     conn = get_db()
     conn.execute('''CREATE TABLE IF NOT EXISTS escalas (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         data_escala TEXT NOT NULL,
         tipo_culto TEXT NOT NULL,
         dirigente TEXT,
         pregador TEXT,
         leitura_palavra TEXT,
         louvor_grupo TEXT,
         diaconos_servico TEXT,
         observacoes TEXT,
         telefone_dirigente TEXT,
         telefone_pregador TEXT,
         igreja_id INTEGER DEFAULT 1
     )''')
     
     igreja_id = session.get('igreja_id', 1)
     conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes, telefone_dirigente, telefone_pregador, igreja_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data_escala, tipo_culto, request.form.get('dirigente', ''),
                   request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                   request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', ''),
                   request.form.get('telefone_dirigente', ''), request.form.get('telefone_pregador', ''), igreja_id))
     conn.commit()
     conn.close()
     flash("Escala de culto registada com sucesso!", "sucesso")
     return redirect('/#aba-escalas')"""

if antigo_bloco in codigo:
    codigo = codigo.replace(antigo_bloco, novo_bloco)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Rota /escalas/novo blindada com sucesso!")
else:
    # Se houver pequenas variações de espaços, substitui via busca dinâmica
    idx_start = codigo.find("@app.route('/escalas/novo'")
    idx_end = codigo.find("@app.route('/escalas/pdf/<int:id>')")
    if idx_start != -1 and idx_end != -1:
        codigo = codigo[:idx_start] + novo_bloco + "\n\n" + codigo[idx_end:]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(codigo)
        print("✓ Rota /escalas/novo localizada e substituída com sucesso!")
    else:
        print("! Não foi possível localizar o bloco exato.")