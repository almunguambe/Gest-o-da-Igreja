with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Bloco de migração que adiciona as colunas com segurança se faltarem
migracao_escalas = """    # Garantir estrutura completa da tabela escalas
    conn.execute('''CREATE TABLE IF NOT EXISTS escalas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_escala TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        dirigente TEXT,
        pregador TEXT,
        leitura_palavra TEXT,
        louvor_grupo TEXT,
        diaconos_servico TEXT,
        observacoes TEXT,
        telefone_dirigente TEXT,
        telefone_pregador TEXT,
        igreja_id INTEGER DEFAULT 1
    )''')
    for col in ['telefone_dirigente', 'telefone_pregador', 'igreja_id']:
        try:
            conn.execute(f"ALTER TABLE escalas ADD COLUMN {col} TEXT")
            conn.commit()
        except Exception:
            pass"""

# Ajuste dentro da rota nova_escala
alvo_antigo = "def nova_escala():"
if alvo_antigo in codigo:
    # Localizar o início da função
    pos = codigo.find(alvo_antigo)
    # Procurar a linha do conn = get_db() logo após
    pos_conn = codigo.find("conn = get_db()", pos)
    if pos_conn != -1 and pos_conn - pos < 400:
        fim_linha_conn = codigo.find("\n", pos_conn)
        codigo = codigo[:fim_linha_conn+1] + migracao_escalas + "\n" + codigo[fim_linha_conn+1:]
        print("✓ Migração adicionada à rota nova_escala!")

# Garantir também na consulta principal (index)
if "todas_escalas = conn.execute(" in codigo:
    idx_consulta = codigo.find("todas_escalas = conn.execute(")
    # Inserir antes da consulta para evitar erros de leitura
    codigo = codigo[:idx_consulta] + migracao_escalas + "\n    " + codigo[idx_consulta:]
    print("✓ Migração adicionada à rota principal!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(codigo)