with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

nova_funcao = '''def obter_caminho_logo():
    # Percorre recursivamente a pasta static para encontrar qualquer imagem de logo
    static_dir = os.path.join(app.root_path, "static")
    if os.path.exists(static_dir):
        for raiz, _, arquivos in os.walk(static_dir):
            for arq in arquivos:
                # Procura por arquivos de imagem comuns usados como logo
                if any(tag in arq.lower() for tag in ["logo", "emblema", "iead", "icone"]) and arq.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return os.path.join(raiz, arq)
    return None
'''

if "def obter_caminho_logo():" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if l.startswith("def obter_caminho_logo():"):
            pulando = True
            novas.append(nova_funcao)
        elif pulando and (l.startswith("@app.") or (l.startswith("def ") and not l.startswith("def obter_caminho_logo"))):
            pulando = False
            novas.append(l)
        elif not pulando:
            novas.append(l)
    conteudo = "\n".join(novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Busca automática e recursiva de logo configurada!")