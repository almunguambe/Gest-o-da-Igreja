with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substituir a criação simples de admin por uma lista com INSERT OR IGNORE
trecho_antigo = """    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                  ('admin', 'chicuque123', 'Pastor Presidente'))"""

trecho_novo = """    # Contas fixas e permanentes da congregação
    contas_permanentes = [
        ('admin', 'chicuque123', 'Pastor Presidente'),
        ('secretaria', '12345', 'Secretário'),
        ('tesouraria', 'senha12345', 'Tesoureiro'),
        ('doutrina', 'senha12345', 'Aluno')
    ]
    for usr, pwd, crg in contas_permanentes:
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (usr, pwd, crg))"""

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✓ Utilizadores permanentes adicionados com sucesso!")
else:
    # Caso haja pequenas variações de linhas
    linhas = conteudo.splitlines()
    novas = []
    ignorar = False
    for l in linhas:
        if 'c.execute("SELECT COUNT(*) FROM usuarios")' in l:
            ignorar = True
            novas.append(trecho_novo)
        elif ignorar and "deptos =" in l:
            ignorar = False
            novas.append(l)
        elif not ignorar:
            novas.append(l)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(novas))
    print("✓ Utilizadores permanentes inseridos!")