with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Substituir o bloco que desenha a linha e o texto do pastor para limitar a largura até antes do QR Code
# O QR Code começa em x = 6.6cm, logo a linha de assinatura deve ficar centrada entre 2.8cm e 6.2cm
import re

# Localizar o desenho da linha e texto do pastor
padrao_antigo = r"c\.line\([^)]+\)\s+c\.drawCentredString\([^,]+,\s*[^,]+,\s*[\"']Pastor Presidente[\"']\)"

substituicao = """# Linha e carimbo do Pastor Presidente ajustados para a esquerda do QR Code
        c.setStrokeColor(colors.HexColor("#64748b"))
        c.setLineWidth(0.5)
        c.line(2.8*cm, 0.7*cm, 6.2*cm, 0.7*cm)
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 5.5)
        c.drawCentredString(4.5*cm, 0.45*cm, "Pastor Presidente")"""

if "Pastor Presidente" in codigo:
    # Ajuste pontual das linhas
    codigo = re.sub(padrao_antigo, substituicao, codigo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Posição da assinatura do Pastor Presidente corrigida!")
else:
    print("! Bloco de assinatura não localizado diretamente.")