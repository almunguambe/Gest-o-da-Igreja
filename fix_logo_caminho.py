with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

nova_funcao_logo = '''def obter_caminho_logo():
    nomes = ["logo.png", "logo.jpg", "logo.jpeg", "logotipo.png", "logotipo.jpg", "iead_logo.png"]
    pastas = [
        os.path.join(app.root_path, "static", "img"),
        os.path.join(app.root_path, "static", "images"),
        os.path.join(app.root_path, "static"),
        app.root_path
    ]
    for pasta in pastas:
        for nome in nomes:
            caminho = os.path.join(pasta, nome)
            if os.path.exists(caminho):
                return caminho
    return None
'''

if "def obter_caminho_logo():" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if l.startswith("def obter_caminho_logo():"):
            pulando = True
            novas.append(nova_funcao_logo)
        elif pulando and (l.startswith("@app.") or l.startswith("def ")):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)
    conteudo = "\n".join(novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Busca de logotipo atualizada com sucesso!")