with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Criação das novas tabelas de configuração no banco
tabelas_config = """
    # Novas tabelas de configuração eclesiástica
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS config_cargos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_cultos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_contas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_atividades (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS igrejas_distritos (id INTEGER PRIMARY KEY AUTOINCREMENT, provincia TEXT, distrito TEXT, nome TEXT)''')
    except:
        pass
"""

if "config_cargos" not in conteudo:
    conteudo = conteudo.replace("c.execute('''CREATE TABLE IF NOT EXISTS membros", tabelas_config + "\n    c.execute('''CREATE TABLE IF NOT EXISTS membros")

# 2. Rotas para adicionar e apagar as novas configurações
rotas_novas_config = '''
# --- ROTAS DE CONFIGURAÇÃO ECLESIÁSTICA EXPANDIDA ---
@app.route('/config/cargo/novo', methods=['POST'])
def config_cargo_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_cargos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/cargo/apagar/<int:id>')
def config_cargo_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_cargos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/culto/novo', methods=['POST'])
def config_culto_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_cultos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/culto/apagar/<int:id>')
def config_culto_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_cultos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/conta/novo', methods=['POST'])
def config_conta_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_contas (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/conta/apagar/<int:id>')
def config_conta_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_contas WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/atividade/novo', methods=['POST'])
def config_atividade_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_atividades (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/atividade/apagar/<int:id>')
def config_atividade_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_atividades WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/igreja/nova', methods=['POST'])
def config_igreja_nova():
    prov = request.form.get('provincia', '').strip()
    dist = request.form.get('distrito', '').strip()
    nome = request.form.get('nome', '').strip()
    if prov and dist and nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO igrejas_distritos (provincia, distrito, nome) VALUES (?, ?, ?)", (prov, dist, nome))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/igreja/apagar/<int:id>')
def config_igreja_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM igrejas_distritos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')
'''

if "/config/cargo/novo" not in conteudo:
    conteudo += "\n" + rotas_novas_config

# 3. Passar as novas listas para a renderização do index
index_pass_old = "lista_categorias=lista_categorias, lista_zonas=lista_zonas"
index_pass_new = "lista_categorias=lista_categorias, lista_zonas=lista_zonas, lista_cargos=lista_cargos, lista_cultos_cfg=lista_cultos_cfg, lista_contas=lista_contas, lista_atividades_cfg=lista_atividades_cfg, lista_igrejas=lista_igrejas"

query_fetch_old = "lista_zonas = conn.execute(\"SELECT * FROM zonas\").fetchall()"
query_fetch_new = """lista_zonas = conn.execute("SELECT * FROM zonas").fetchall()
    try:
        lista_cargos = conn.execute("SELECT * FROM config_cargos ORDER BY nome").fetchall()
    except: lista_cargos = []
    try:
        lista_cultos_cfg = conn.execute("SELECT * FROM config_cultos ORDER BY nome").fetchall()
    except: lista_cultos_cfg = []
    try:
        lista_contas = conn.execute("SELECT * FROM config_contas ORDER BY nome").fetchall()
    except: lista_contas = []
    try:
        lista_atividades_cfg = conn.execute("SELECT * FROM config_atividades ORDER BY nome").fetchall()
    except: lista_atividades_cfg = []
    try:
        lista_igrejas = conn.execute("SELECT * FROM igrejas_distritos ORDER BY provincia, distrito, nome").fetchall()
    except: lista_igrejas = []"""

if query_fetch_old in conteudo:
    conteudo = conteudo.replace(query_fetch_old, query_fetch_new)

if index_pass_old in conteudo:
    conteudo = conteudo.replace(index_pass_old, index_pass_new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ app.py atualizado com tabelas e rotas para Províncias, Distritos e novas Configurações!")