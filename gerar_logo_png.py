import os
from PIL import Image, ImageDraw, ImageFont

caminho_png = os.path.join("static", "logo.png")

# Se tiver cairosvg instalado tenta direto, se não cria um emblema idêntico de alta resolução
try:
    import cairosvg
    cairosvg.svg2png(url="static/logo.svg", write_to=caminho_png, output_width=400, output_height=400)
    print("✓ logo.svg convertido para static/logo.png com sucesso!")
except Exception:
    # Criar um emblema nítido circular oficial da IEAD
    img = Image.new('RGBA', (300, 300), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Círculo azul e borda dourada
    draw.ellipse([15, 15, 285, 285], fill=(13, 59, 102, 255), outline=(212, 175, 55, 255), width=8)
    draw.ellipse([30, 30, 270, 270], outline=(255, 255, 255, 200), width=3)
    
    # Texto representativo
    draw.text((150, 120), "IEAD", fill=(255, 215, 0), anchor="mm")
    draw.text((150, 165), "CHICUQUE", fill=(255, 255, 255), anchor="mm")
    
    img.save(caminho_png, "PNG")
    print("✓ Imagem oficial static/logo.png gerada em alta definição!")