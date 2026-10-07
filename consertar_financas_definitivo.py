with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# Localizar e substituir a função novo_financeiro inteira
padrao = r"@app\.route\('/financeiro/novo', methods=\['POST'\]\)\s*def novo_financeiro\(\):.*?(?=@app\.route|\Z)"

novo_codigo = '''@app.route('/financeiro/novo', methods=['POST'])
def novo_financeiro():
    if not can_tesouraria(): return redirect('/')
    data_raw = request.form.get('data_movimento') or datetime.now().strftime("%Y-%m-%d")
    dt_obj = datetime.strptime(data_raw, "%Y-%m-%d")
    conn = get_db()
    metodo = request.form.get('metodo_pagamento', 'Dinheiro')
    referencia = request.form.get('referencia_transacao', '').strip() or None

    # Auto-cura: Garantir que as colunas existam na tabela antes de inserir
    try:
        conn.execute("ALTER TABLE financeiro ADD COLUMN metodo_pagamento TEXT DEFAULT 'Dinheiro'")
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute("ALTER TABLE financeiro ADD COLUMN referencia_transacao TEXT")
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute(\'\'\'INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao, metodo_pagamento, referencia_transacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\'\'\',
                     (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                      request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                      datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao'], metodo, referencia))
        conn.commit()
    except Exception as e:
        # Fallback de seguranca caso ocorra qualquer restricao com as novas colunas
        conn.execute(\'\'\'INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\'\'\',
                     (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                      request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                      datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao']))
        conn.commit()
    finally:
        conn.close()
    return redirect('/')

'''

conteudo = re.sub(padrao, novo_codigo, conteudo, count=1, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Rota novo_financeiro corrigida com auto-cura e fallback ativo!")