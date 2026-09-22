with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Redirecionar a rota de estudos diretamente para o currículo da Classe I
bloco_rota_estudos = '''@app.route('/estudos')
def estudos():
    from flask import redirect
    return redirect('/discipulado/classe/c1')
'''

if "@app.route('/estudos')" in conteudo:
    partes = conteudo.split("@app.route('/estudos')")
    topo = partes[0]
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + bloco_rota_estudos + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Rota /estudos conectada ao currículo dinâmico das 4 classes!")