with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

funcao_logo_definitiva = '''def obter_caminho_logo():
    caminho = os.path.join(app.root_path, "static", "logo.png")
    if os.path.exists(caminho):
        return caminho
    caminho_rel = os.path.join("static", "logo.png")
    if os.path.exists(caminho_rel):
        return os.path.abspath(caminho_rel)
    return None
'''

if "def obter_caminho_logo():" in conteudo:
    partes = conteudo.split("def obter_caminho_logo():")
    topo = partes[0]
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + funcao_logo_definitiva + "\n@app." + resto[1]

# Substitui eventuais chamadas complexas de carregar_flowable_logo para RLImage direta
conteudo = conteudo.replace("carregar_flowable_logo(70, 70)", "RLImage(obter_caminho_logo(), width=70, height=70) if obter_caminho_logo() else None")
conteudo = conteudo.replace("carregar_flowable_logo(65, 65)", "RLImage(obter_caminho_logo(), width=65, height=65) if obter_caminho_logo() else None")
conteudo = conteudo.replace("carregar_flowable_logo(60, 60)", "RLImage(obter_caminho_logo(), width=60, height=60) if obter_caminho_logo() else None")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Caminho de logo fixado diretamente para static/logo.png!")