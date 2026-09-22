with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Trecho exato com recuo incorreto e conn.close() prematuro
trecho_antigo = """    conn.close()

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)


        # Carregar dúvidas bíblicas para o painel pastoral
        duvidas_lista = []
        candidatos_discipulado = []
        try:
            c.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
            duvidas_lista = c.fetchall()
        except Exception:
            pass

        try:
            query_prog = \"\"\"
                SELECT m.id, m.nome, m.foto_path, m.telefone,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
                FROM membros m
                LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
                GROUP BY m.id, m.nome, m.foto_path, m.telefone
                ORDER BY m.id DESC
            \"\"\"
            c.execute(query_prog)
            candidatos_discipulado = c.fetchall()
        except Exception:
            pass"""

# Trecho com alinhamento correto de 4 espaços e conn.close() após as consultas
trecho_correto = """    # Carregar dúvidas bíblicas para o painel pastoral
    duvidas_lista = []
    candidatos_discipulado = []
    try:
        c.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
        duvidas_lista = c.fetchall()
    except Exception:
        pass

    try:
        query_prog = \"\"\"
            SELECT m.id, m.nome, m.foto_path, m.telefone,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
            FROM membros m
            LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
            GROUP BY m.id, m.nome, m.foto_path, m.telefone
            ORDER BY m.id DESC
        \"\"\"
        c.execute(query_prog)
        candidatos_discipulado = c.fetchall()
    except Exception:
        pass

    conn.close()

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)"""

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_correto)
else:
    # Caso haja variações de quebra de linha do Bloco de Notas
    linhas = conteudo.splitlines()
    linhas_novas = []
    ignorar = False
    for l in linhas:
        if "duvidas_lista = []" in l:
            ignorar = True
            # Adiciona o bloco com 4 espaços antes de fechar o conn
            linhas_novas.append(trecho_correto)
        elif ignorar and ("alerta_duplicado =" in l or "return render_template" in l):
            ignorar = False
            if "alerta_duplicado =" not in trecho_correto:
                linhas_novas.append(l)
        elif not ignorar and "conn.close()" in l and "membros_json" in "".join(linhas_novas[-5:]):
            # pula o conn.close antigo porque ele já está no bloco novo
            continue
        elif not ignorar:
            linhas_novas.append(l)
    conteudo = "\n".join(linhas_novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Indentação corrigida para 4 espaços e consultas reposicionadas antes do conn.close()!")