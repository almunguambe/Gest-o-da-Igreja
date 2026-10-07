with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

antigo = """    conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['data_escala'], request.form['tipo_culto'], request.form.get('dirigente', ''),
                  request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                  request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', '')))"""

novo = """    igreja_id = session.get('igreja_id', 1)
    conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes, telefone_dirigente, telefone_pregador, igreja_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['data_escala'], request.form['tipo_culto'], request.form.get('dirigente', ''),
                  request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                  request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', ''),
                  request.form.get('telefone_dirigente', ''), request.form.get('telefone_pregador', ''), igreja_id))"""

if antigo in conteudo:
    conteudo = conteudo.replace(antigo, novo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Rota /escalas/novo atualizada com sucesso!")
else:
    print("! Trecho exato não encontrado. Verifique as quebras de linha.")