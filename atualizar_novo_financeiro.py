with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

antigo_bloco = """    conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                  request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                  datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao']))"""

novo_bloco = """    metodo = request.form.get('metodo_pagamento', 'Dinheiro')
    referencia = request.form.get('referencia_transacao', '').strip() or None
    conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao, metodo_pagamento, referencia_transacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                  request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                  datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao'], metodo, referencia))"""

if antigo_bloco in codigo:
    codigo = codigo.replace(antigo_bloco, novo_bloco, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Rota /financeiro/novo atualizada com suporte a métodos digitais!")
else:
    print("! Bloco antigo não encontrado para substituição exata.")