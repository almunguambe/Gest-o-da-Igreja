with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Substitui redirect(url_for('portal_estudos')) por redirect('/estudos') nas linhas de login e dashboard
conteudo = conteudo.replace("url_for('portal_estudos')", "'/estudos'")

# 2. Adiciona alias de rota para /portal_estudos garantindo compatibilidade total
alias_rota = """
@app.route('/portal_estudos')
def portal_estudos():
    return redirect('/estudos')
"""

if "@app.route('/portal_estudos')" not in conteudo:
    alvo = "@app.route('/estudos')"
    conteudo = conteudo.replace(alvo, alias_rota + "\n" + alvo)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Redirecionamento do aluno corrigido para a rota /estudos!")