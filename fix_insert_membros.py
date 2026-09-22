with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

bloco_antigo_insert = """    conn.execute('''
        INSERT INTO membros (
            nome, telefone, genero, data_nascimento, faixa_etaria,
            naturalidade, bairro, filiacao, tipo_documento, numero_documento,
            ano_conversao, data_batismo, posicao_atual, progressoes,
            departamento, foto_path, observacoes, data_registo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nome, request.form.get('telefone', '').strip(), request.form.get('genero', 'Masculino'),
        request.form.get('data_nascimento', ''), request.form.get('faixa_etaria', 'Adulto'),
        request.form.get('naturalidade', '').strip(), request.form.get('bairro', ''),
        request.form.get('filiacao', '').strip(), tipo_doc, num_doc, ano_conv_val,
        request.form.get('data_batismo', ''), request.form.get('posicao_atual', 'Membro em Comunhão'),
        request.form.get('progressoes', '').strip(), request.form.get('departamento', 'Geral'),
        foto_path, request.form.get('observacoes', '').strip(), datetime.now().strftime("%d/%m/%Y")
    ))
    conn.commit()
    conn.close()"""

bloco_novo_insert = """    # Verificação obrigatória do campo Zona
    if not zona:
        conn.close()
        session['alerta_duplicado'] = "O campo Zona é de preenchimento obrigatório."
        return redirect(url_for('dashboard'))

    c = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    marcador = "%s" if is_pg else "?"

    sql_insert = f\"\"\"
        INSERT INTO membros (
            nome, telefone, genero, data_nascimento, faixa_etaria,
            naturalidade, bairro, zona, celula, distrito,
            filiacao, tipo_documento, numero_documento,
            ano_conversao, data_batismo, posicao_atual, progressoes,
            departamento, foto_path, observacoes, data_registo, estado
        ) VALUES ({', '.join([marcador]*22)})
    \"\"\"

    valores = (
        nome, request.form.get('telefone', '').strip(), request.form.get('genero', 'Masculino'),
        request.form.get('data_nascimento', ''), request.form.get('faixa_etaria', 'Adulto'),
        request.form.get('naturalidade', '').strip(), request.form.get('bairro', '').strip(),
        zona, celula, distrito,
        request.form.get('filiacao', '').strip(), tipo_doc, num_doc, ano_conv_val,
        request.form.get('data_batismo', ''), request.form.get('posicao_atual', 'Membro em Comunhão'),
        request.form.get('progressoes', '').strip(), request.form.get('departamento', 'Geral'),
        foto_path, request.form.get('observacoes', '').strip(), datetime.now().strftime("%d/%m/%Y"),
        'Activo'
    )

    if is_pg:
        c.execute(sql_insert, valores)
    else:
        conn.execute(sql_insert, valores)

    conn.commit()
    conn.close()"""

if bloco_antigo_insert in conteudo:
    conteudo = conteudo.replace(bloco_antigo_insert, bloco_novo_insert)
else:
    # Substituição por linhas caso haja diferença de espaçamento
    inicio_str = "ano_conv_val = int(ano_conv) if ano_conv and ano_conv.isdigit() else None"
    fim_str = "session['sucesso_cadastro'] = f\"Membro '{nome}' registado com sucesso!\""
    if inicio_str in conteudo and fim_str in conteudo:
        partes_ini = conteudo.split(inicio_str)
        partes_fim = partes_ini[1].split(fim_str)
        conteudo = partes_ini[0] + inicio_str + "\n\n" + bloco_novo_insert + "\n    " + fim_str + partes_fim[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Inserção de membros atualizada com suporte a Zona (obrigatória), Célula, Bairro e Distrito!")