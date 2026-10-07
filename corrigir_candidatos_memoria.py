with open('app.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Vamos inspecionar e substituir o trecho entre a linha 847 e 870
inicio = -1
fim = -1

for i, l in enumerate(linhas):
    if '# Buscar Candidatos ao Batismo' in l or 'candidatos_batismo = []' in l:
        if inicio == -1:
            inicio = i
    if 'return render_template(\'dashboard.html\'' in l:
        fim = i
        break

if inicio != -1 and fim != -1:
    bloco_substituto = """    # Filtrar Candidatos ao Batismo diretamente da lista oficial de membros em memoria
    candidatos_batismo = []
    for m in todos_membros:
        # Suporta dicionario (PostgreSQL/RealDictCursor) e sqlite3.Row
        f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
        b_val = str(m.get('batizado', '') if hasattr(m, 'get') else m['batizado'] if 'batizado' in m.keys() else '').lower()
        
        # Considera candidatos ao batismo, membros em prova ou nao batizados
        if ('candidat' in f_val) or ('prova' in f_val) or ('convertid' in f_val) or (b_val in ['nao', 'não', 'pendente', '']):
            candidatos_batismo.append(m)

    # Se a lista filtrada estiver vazia, disponibiliza todos os membros para permitir selecao imediata
    if not candidatos_batismo:
        candidatos_batismo = todos_membros

"""
    linhas[inicio:fim] = [bloco_substituto]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✓ app.py corrigido com sucesso! Candidatos agora sao extraidos diretamente de todos_membros.")
else:
    print(f"Indices nao localizados: inicio={inicio}, fim={fim}")