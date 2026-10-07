with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Injetar a criação da tabela igrejas dentro de init_db()
trecho_init_db = "def init_db():\n    conn = get_db()\n    c = conn.cursor()"
novo_init_db = """def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS igrejas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        cidade TEXT,
        distrito TEXT,
        pastor TEXT,
        telefone TEXT,
        ativa INTEGER DEFAULT 1,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("SELECT id FROM igrejas WHERE id = 1")
    if not c.fetchone():
        c.execute("INSERT INTO igrejas (id, nome, cidade, distrito, pastor, telefone, ativa) VALUES (1, 'Congregação de Chicuque', 'Maxixe', 'Maxixe', 'Pastor Local', '+258 84 000 0000', 1)")"""

if trecho_init_db in conteudo and "CREATE TABLE IF NOT EXISTS igrejas" not in conteudo:
    conteudo = conteudo.replace(trecho_init_db, novo_init_db, 1)
    print("✓ init_db() atualizado com a tabela igrejas!")

# 2. Atualizar a rota /login para preencher igreja_id, igreja_nome e is_superadmin
trecho_login = """        if user:
            session['usuario'] = user['usuario']
            session['cargo'] = user['cargo']
            if user['cargo'] == 'Estudante':
                return redirect(url_for('portal_estudos'))
            return redirect(url_for('dashboard'))"""

novo_login = """        if user:
            session['usuario'] = user['usuario']
            session['cargo'] = user['cargo']
            
            # Contexto Multi-Igreja
            igreja_id = user['igreja_id'] if ('igreja_id' in user.keys() and user['igreja_id']) else 1
            session['igreja_id'] = igreja_id
            session['is_superadmin'] = bool(user['is_superadmin']) if 'is_superadmin' in user.keys() else False

            conn_ig = get_db()
            ig_info = conn_ig.execute('SELECT nome FROM igrejas WHERE id = ?', (igreja_id,)).fetchone()
            conn_ig.close()
            session['igreja_nome'] = ig_info['nome'] if ig_info else 'IEAD - Congregação Local'

            if user['cargo'] == 'Estudante':
                return redirect(url_for('portal_estudos'))
            return redirect(url_for('dashboard'))"""

if trecho_login in conteudo:
    conteudo = conteudo.replace(trecho_login, novo_login, 1)
    print("✓ Rota /login atualizada para carregar a congregação dinamicamente!")
else:
    print("- Trecho do login já atualizado ou modificado.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("--- ATUALIZACAO CONCLUIDA ---")