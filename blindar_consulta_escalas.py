with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. Garantir que a tabela escalas exista antes da consulta na rota principal
antigo = 'todas_escalas = conn.execute("SELECT * FROM escalas WHERE igreja_id = ? ORDER BY data_escala DESC LIMIT 20", (igreja_id,)).fetchall()'

novo = '''conn.execute("""CREATE TABLE IF NOT EXISTS escalas (
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
    )""")
    todas_escalas = conn.execute("SELECT * FROM escalas WHERE igreja_id = ? ORDER BY data_escala DESC LIMIT 20", (igreja_id,)).fetchall()'''

if antigo in codigo:
    codigo = codigo.replace(antigo, novo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Consulta de escalas protegida com criação de tabela automática!")
else:
    print("! Bloco da consulta não encontrado exatamente como o padrão.")