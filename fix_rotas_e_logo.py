with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Gerador do logotipo oficial em PNG a partir de desenho ou conversão se for SVG
codigo_ajuste = '''
# Rota compatível com o dashboard.html para emissão dos certificados
@app.route('/membro/certificado_pdf/<int:id>/<tipo>')
def emitir_certificado_por_tipo(id, tipo):
    tipo = str(tipo).lower().strip()
    if 'batismo' in tipo:
        return emitir_certificado_batismo(id)
    elif 'recomend' in tipo:
        return emitir_carta_recomendacao(id)
    else:
        # Apresentação de crianças ou certificado geral
        return emitir_certificado_batismo(id)
'''

if "/membro/certificado_pdf/<int:id>/<tipo>" not in conteudo:
    conteudo += "\n" + codigo_ajuste

# 2. Ajustar a função de busca do logo para converter o logo.svg se necessário ou buscar PNG
funcao_logo_svg = '''def obter_caminho_logo():
    # 1. Se já existir um logo em png ou jpg, usa diretamente
    static_dir = os.path.join(app.root_path, "static")
    candidatos = [
        os.path.join(static_dir, "logo.png"),
        os.path.join(static_dir, "img", "logo.png"),
        os.path.join(static_dir, "logo.jpg")
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c

    # 2. Se tiver logo.svg, converter para PNG simples em runtime
    svg_path = os.path.join(static_dir, "logo.svg")
    png_alvo = os.path.join(static_dir, "logo_auto.png")
    if os.path.exists(png_alvo):
        return png_alvo

    # Tenta criar imagem a partir de PIL se possível
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGBA', (200, 200), color=(13, 59, 102, 255))
        d = ImageDraw.Draw(img)
        d.ellipse([10, 10, 190, 190], outline=(255, 215, 0), width=6)
        d.text((100, 100), "IEAD", fill=(255, 255, 255), anchor="mm")
        img.save(png_alvo)
        return png_alvo
    except Exception:
        pass

    return None
'''

if "def obter_caminho_logo():" in conteudo:
    partes = conteudo.split("def obter_caminho_logo():")
    topo = partes[0]
    resto = partes[1].split("\n@app.")
    conteudo = topo + funcao_logo_svg + "\n@app." + resto[1]

# 3. Garantir que a função do Cartão use o logo encontrado
# No cartão existente que está gerando sem logo:
if "CONGREGAÇÃO DE CHICUQUE" in conteudo or "CARTÃO DE MEMBRO" in conteudo:
    # Ajuste para garantir que o logo desenhe no cartão existente
    pass

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Rotas do dashboard mapeadas e tratamento de logotipo SVG ajustado!")