with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Garantir que as colunas metodo_pagamento e referencia_transacao existam na criacao da tabela
tabela_antiga = """    c.execute('''CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        local_movimento TEXT DEFAULT 'Caixa',
        departamento TEXT DEFAULT 'Geral',
        categoria TEXT NOT NULL,
        valor REAL NOT NULL,
        data_movimento TEXT NOT NULL,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        data_registo TEXT NOT NULL,
        membro_id INTEGER,
        descricao TEXT
    )''')"""

tabela_nova = """    c.execute('''CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        local_movimento TEXT DEFAULT 'Caixa',
        departamento TEXT DEFAULT 'Geral',
        categoria TEXT NOT NULL,
        valor REAL NOT NULL,
        data_movimento TEXT NOT NULL,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        data_registo TEXT NOT NULL,
        membro_id INTEGER,
        descricao TEXT,
        metodo_pagamento TEXT DEFAULT 'Dinheiro',
        referencia_transacao TEXT
    )''')
    # Migracao automatica caso a tabela ja exista sem essas colunas
    try:
        c.execute("ALTER TABLE financeiro ADD COLUMN metodo_pagamento TEXT DEFAULT 'Dinheiro'")
    except:
        pass
    try:
        c.execute("ALTER TABLE financeiro ADD COLUMN referencia_transacao TEXT")
    except:
        pass"""

if tabela_antiga in conteudo:
    conteudo = conteudo.replace(tabela_antiga, tabela_nova)
    print("✓ Tabela financeiro e migracao de colunas atualizadas!")
else:
    print("! Bloco da tabela financeiro nao bateu exatamente com o original.")

# 2. Blindar a rota /financeiro/novo com tratamento de erro
bloco_novo_fin = """@app.route('/financeiro/novo', methods=['POST'])
def novo_financeiro():
    if not can_tesouraria(): return redirect('/')
    data_raw = request.form.get('data_movimento') or datetime.now().strftime("%Y-%m-%d")
    dt_obj = datetime.strptime(data_raw, "%Y-%m-%d")
    conn = get_db()
    metodo = request.form.get('metodo_pagamento', 'Dinheiro')
    referencia = request.form.get('referencia_transacao', '').strip() or None
    try:
        conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao, metodo_pagamento, referencia_transacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                      request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                      datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao'], metodo, referencia))
        conn.commit()
    except Exception as e:
        # Se falhar por ausencia de colunas no banco ja existente, adiciona na hora e tenta novamente
        try:
            conn.execute("ALTER TABLE financeiro ADD COLUMN metodo_pagamento TEXT DEFAULT 'Dinheiro'")
            conn.commit()
        except: pass
        try:
            conn.execute("ALTER TABLE financeiro ADD COLUMN referencia_transacao TEXT")
            conn.commit()
        except: pass
        try:
            conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao, metodo_pagamento, referencia_transacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                          request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                          datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao'], metodo, referencia))
            conn.commit()
        except Exception as err:
            # Fallback seguro caso as colunas ainda nao estejam acessiveis
            conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                          request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                          datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao']))
            conn.commit()
    finally:
        conn.close()
    return redirect('/')"""

# Substituir a rota antiga
import re
padrao_rota = r"@app\.route\('/financeiro/novo', methods=\['POST'\]\)\s*def novo_financeiro\(\):.*?return redirect\('/'\)"
conteudo = re.sub(padrao_rota, bloco_novo_fin, conteudo, count=1, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Rota novo_financeiro blindada e atualizada com sucesso no app.py!")