with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Substituir a tabela cultos_frequencia para ter as novas colunas
tabela_antiga = """c.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_culto TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        homens INTEGER DEFAULT 0,
        mulheres INTEGER DEFAULT 0,
        jovens INTEGER DEFAULT 0,
        criancas INTEGER DEFAULT 0,
        visitantes INTEGER DEFAULT 0,
        novos_convertidos INTEGER DEFAULT 0,
        total_presentes INTEGER DEFAULT 0,
        pregador TEXT,
        tema_mensagem TEXT,
        data_registo TEXT NOT NULL
    )''')"""

tabela_nova = """c.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_culto TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        homens INTEGER DEFAULT 0,
        mulheres INTEGER DEFAULT 0,
        jovens_homens INTEGER DEFAULT 0,
        jovens_mulheres INTEGER DEFAULT 0,
        jovens INTEGER DEFAULT 0,
        criancas_meninos INTEGER DEFAULT 0,
        criancas_meninas INTEGER DEFAULT 0,
        criancas INTEGER DEFAULT 0,
        visitantes_homens INTEGER DEFAULT 0,
        visitantes_mulheres INTEGER DEFAULT 0,
        visitantes INTEGER DEFAULT 0,
        novos_convertidos INTEGER DEFAULT 0,
        total_presentes INTEGER DEFAULT 0,
        pregador TEXT,
        tema_mensagem TEXT,
        data_registo TEXT NOT NULL
    )''')
    for col in ['jovens_homens', 'jovens_mulheres', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres']:
        try: c.execute(f"ALTER TABLE cultos_frequencia ADD COLUMN {col} INTEGER DEFAULT 0")
        except: pass"""

if tabela_antiga in conteudo:
    conteudo = conteudo.replace(tabela_antiga, tabela_nova)

# 2. Substituir a rota /cultos/novo
padrao_rota = r"@app\.route\('/cultos/novo', methods=\['POST'\]\)\s*def novo_culto\(\):.*?(?=@app\.route|\Z)"

nova_rota = '''@app.route('/cultos/novo', methods=['POST'])
def novo_culto():
    if not can_cadastro(): return redirect('/')
    h = int(request.form.get('homens') or 0)
    m = int(request.form.get('mulheres') or 0)
    jh = int(request.form.get('jovens_homens') or 0)
    jm = int(request.form.get('jovens_mulheres') or 0)
    cm = int(request.form.get('criancas_meninos') or 0)
    cf = int(request.form.get('criancas_meninas') or 0)
    vh = int(request.form.get('visitantes_homens') or 0)
    vf = int(request.form.get('visitantes_mulheres') or 0)
    nc = int(request.form.get('novos_convertidos') or 0)

    j_total = jh + jm
    c_total = cm + cf
    v_total = vh + vf
    total = h + m + j_total + c_total + v_total

    conn = get_db()
    # Auto-cura de colunas caso nao existam na tabela ativa
    for col in ['jovens_homens', 'jovens_mulheres', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres']:
        try:
            conn.execute(f"ALTER TABLE cultos_frequencia ADD COLUMN {col} INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            pass

    try:
        conn.execute(\'\'\'INSERT INTO cultos_frequencia (data_culto, tipo_culto, homens, mulheres, jovens_homens, jovens_mulheres, jovens, criancas_meninos, criancas_meninas, criancas, visitantes_homens, visitantes_mulheres, visitantes, novos_convertidos, total_presentes, pregador, tema_mensagem, data_registo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\'\'\',
                     (request.form['data_culto'], request.form['tipo_culto'], h, m, jh, jm, j_total, cm, cf, c_total, vh, vf, v_total, nc, total,
                      request.form.get('pregador', ''), request.form.get('tema_mensagem', ''), datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
    except Exception as e:
        # Fallback de compatibilidade
        conn.execute(\'\'\'INSERT INTO cultos_frequencia (data_culto, tipo_culto, homens, mulheres, jovens, criancas, visitantes, novos_convertidos, total_presentes, pregador, tema_mensagem, data_registo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\'\'\',
                     (request.form['data_culto'], request.form['tipo_culto'], h, m, j_total, c_total, v_total, nc, total,
                      request.form.get('pregador', ''), request.form.get('tema_mensagem', ''), datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
    finally:
        conn.close()

    session['sucesso_cadastro'] = "Culto e frequência registados!"
    return redirect('/')

'''

conteudo = re.sub(padrao_rota, nova_rota, conteudo, count=1, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ app.py atualizado com novos campos de cultos e auto-cura!")