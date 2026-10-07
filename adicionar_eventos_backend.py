with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Tabela config_eventos
tabela_eventos = """
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS config_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    except: pass
"""
if "config_eventos" not in conteudo:
    conteudo = conteudo.replace("c.execute('''CREATE TABLE IF NOT EXISTS membros", tabela_eventos + "\n    c.execute('''CREATE TABLE IF NOT EXISTS membros")

# 2. Rotas para adicionar e apagar Tipos de Eventos
rotas_eventos = '''
@app.route('/config/evento/novo', methods=['POST'])
def config_evento_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_eventos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/evento/apagar/<int:id>')
def config_evento_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_eventos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')
'''
if "/config/evento/novo" not in conteudo:
    conteudo += "\n" + rotas_eventos

# 3. Consulta de lista_eventos_cfg
if "lista_eventos_cfg" not in conteudo:
    busca_eventos = """
    try:
        lista_eventos_cfg = conn.execute("SELECT * FROM config_eventos ORDER BY nome").fetchall()
    except: lista_eventos_cfg = []
    """
    conteudo = conteudo.replace('lista_atividades_cfg = []', 'lista_atividades_cfg = []' + busca_eventos)
    conteudo = conteudo.replace('lista_atividades_cfg=lista_atividades_cfg,', 'lista_atividades_cfg=lista_atividades_cfg, lista_eventos_cfg=lista_eventos_cfg,')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ app.py atualizado com suporte a Tipos de Eventos!")