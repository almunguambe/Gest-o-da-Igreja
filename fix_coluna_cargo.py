with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substitui a consulta que exige a coluna 'cargo' por uma consulta segura
antiga_query = "SELECT id, nome, cargo, congregacao, data_batismo FROM membros"
nova_query = "SELECT * FROM membros"

if antiga_query in conteudo:
    conteudo = conteudo.replace(antiga_query, nova_query)

# Ajuste no tratamento dos campos para não depender de cargo
codigo_extracao_antigo = """        if isinstance(membro, dict):
            nome = membro.get('nome') or "MEMBRO"
            data_bat = membro.get('data_batismo')
            congregacao = membro.get('congregacao') or "Chicuque"
        else:
            nome = membro[1]
            data_bat = membro[4]
            congregacao = membro[3] or "Chicuque" """

codigo_extracao_novo = """        if isinstance(membro, dict):
            nome = membro.get('nome') or "MEMBRO"
            data_bat = membro.get('data_batismo')
            congregacao = membro.get('congregacao') or "Chicuque Sede"
        else:
            try:
                nome = membro['nome']
                data_bat = membro['data_batismo']
                congregacao = membro['congregacao'] if 'congregacao' in membro.keys() else "Chicuque Sede"
            except Exception:
                nome = membro[1] if len(membro) > 1 else "MEMBRO"
                data_bat = membro[2] if len(membro) > 2 else ""
                congregacao = "Chicuque Sede" """

# Se encontrar o trecho antigo, substitui
if "SELECT id, nome, cargo" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    for l in linhas:
        if "SELECT id, nome, cargo, congregacao, data_batismo FROM membros" in l:
            l = l.replace("SELECT id, nome, cargo, congregacao, data_batismo FROM membros", "SELECT * FROM membros")
        novas.append(l)
    conteudo = "\n".join(novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Consulta SQL corrigida para não exigir a coluna 'cargo'!")