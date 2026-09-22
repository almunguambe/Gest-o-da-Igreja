with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substitui o trecho de desenho do cabeçalho do cartão para incluir a imagem do logo
bloco_logo_cartao = '''
        # Inserção do Logo Oficial no Cartão
        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                # Desenha o logo proporcional no canto superior esquerdo ou central
                c.drawImage(logo_path, x_inicio + 10, y_topo - 45, width=40, height=40, preserveAspectRatio=True, mask='auto')
            except Exception as err:
                print(f"Aviso logo cartao: {err}")
'''

# Se existir a função gerar_cartao_membro_pdf ou similar
if "def gerar_cartao_membro" in conteudo or "cartao_membro" in conteudo:
    linhas = conteudo.splitlines()
    linhas_novas = []
    dentro_cartao = False
    logo_adicionado = False

    for l in linhas:
        if "def " in l and "cartao" in l.lower():
            dentro_cartao = True
        elif dentro_cartao and ("c.setFont(" in l or "c.drawString(" in l) and not logo_adicionado:
            linhas_novas.append(bloco_logo_cartao)
            logo_adicionado = True
        elif dentro_cartao and l.startswith("def "):
            dentro_cartao = False
        linhas_novas.append(l)
    
    conteudo = "\n".join(linhas_novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Logótipo inserido na rotina do cartão de membro!")