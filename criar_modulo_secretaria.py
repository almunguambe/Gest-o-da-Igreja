with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Adicionar criação da tabela de planificação no app.py
tabela_plan = """
    c.execute('''CREATE TABLE IF NOT EXISTS actividades_planeamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departamento TEXT NOT NULL,
        actividade TEXT NOT NULL,
        tipo_evento TEXT DEFAULT 'Geral',
        data_prevista TEXT NOT NULL,
        frequencia TEXT DEFAULT 'Pontual',
        responsavel TEXT NOT NULL,
        contacto_responsavel TEXT,
        status TEXT DEFAULT 'Planeado',
        data_realizacao TEXT,
        temas_abordados TEXT,
        homens_participantes INTEGER DEFAULT 0,
        mulheres_participantes INTEGER DEFAULT 0,
        jovens_participantes INTEGER DEFAULT 0,
        criancas_participantes INTEGER DEFAULT 0,
        pessoas_alcancadas INTEGER DEFAULT 0,
        decisoes_convertidos INTEGER DEFAULT 0,
        relatorio_observacoes TEXT,
        data_registo TEXT
    )''')
"""

if 'CREATE TABLE IF NOT EXISTS actividades_planeamento' not in conteudo:
    # Inserir antes da criação de cultos_frequencia
    conteudo = conteudo.replace("c.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia", tabela_plan + "\n    c.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia")
    print("✓ Tabela actividades_planeamento inserida na inicialização do app.py!")

# 2. Adicionar as rotas da Secretaria e Planificação no app.py
novas_rotas = '''
# ==========================================
# ROTAS DA SECRETARIA & PLANIFICAÇÃO (MODELO OFICIAL IEAD)
# ==========================================
@app.route('/secretaria/planificacao/nova', methods=['POST'])
def nova_actividade_planificada():
    conn = get_db()
    try:
        conn.execute("ALTER TABLE actividades_planeamento ADD COLUMN tipo_evento TEXT DEFAULT 'Geral'")
        conn.commit()
    except: pass
    
    conn.execute(\'\'\'INSERT INTO actividades_planeamento 
        (departamento, actividade, tipo_evento, data_prevista, frequencia, responsavel, contacto_responsavel, status, data_registo)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Planeado', ?)\'\'\',
        (request.form['departamento'], request.form['actividade'], request.form.get('tipo_evento', 'Geral'),
         request.form['data_prevista'], request.form.get('frequencia', 'Pontual'), request.form['responsavel'],
         request.form.get('contacto_responsavel', ''), datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return redirect('/#aba-secretaria')

@app.route('/secretaria/planificacao/relatar/<int:act_id>', methods=['POST'])
def relatar_actividade_planificada(act_id):
    conn = get_db()
    status = request.form.get('status', 'Realizado')
    data_real = request.form.get('data_realizacao') or datetime.now().strftime("%Y-%m-%d")
    temas = request.form.get('temas_abordados', '')
    h = int(request.form.get('homens_participantes') or 0)
    m = int(request.form.get('mulheres_participantes') or 0)
    j = int(request.form.get('jovens_participantes') or 0)
    c = int(request.form.get('criancas_participantes') or 0)
    alcancadas = int(request.form.get('pessoas_alcancadas') or 0)
    decisoes = int(request.form.get('decisoes_convertidos') or 0)
    obs = request.form.get('relatorio_observacoes', '')

    conn.execute(\'\'\'UPDATE actividades_planeamento SET 
        status = ?, data_realizacao = ?, temas_abordados = ?, 
        homens_participantes = ?, mulheres_participantes = ?, jovens_participantes = ?, criancas_participantes = ?,
        pessoas_alcancadas = ?, decisoes_convertidos = ?, relatorio_observacoes = ?
        WHERE id = ?\'\'\',
        (status, data_real, temas, h, m, j, c, alcancadas, decisoes, obs, act_id))
    conn.commit()
    conn.close()
    return redirect('/#aba-secretaria')

@app.route('/secretaria/relatorio_oficial')
def ver_relatorio_oficial():
    conn = get_db()
    # Coleta membros por categoria para o modelo oficial
    membros = conn.execute("SELECT * FROM membros").fetchall()
    cultos = conn.execute("SELECT * FROM cultos_frequencia ORDER BY id DESC").fetchall()
    planos = conn.execute("SELECT * FROM actividades_planeamento ORDER BY id DESC").fetchall()
    casamentos = conn.execute("SELECT * FROM casamentos").fetchall()
    
    return render_template('relatorio_oficial_modelo.html', membros=membros, cultos=cultos, planos=planos, casamentos=casamentos)
'''

if '/secretaria/planificacao/nova' not in conteudo:
    conteudo += "\n" + novas_rotas
    print("✓ Rotas da Secretaria e Planificação inseridas no app.py!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)
'''