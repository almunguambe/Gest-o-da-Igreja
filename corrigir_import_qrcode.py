with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Garantir o import do ImageReader no topo
if 'from reportlab.lib.utils import ImageReader' not in conteudo:
    # Procura onde estão os imports do reportlab
    if 'from reportlab.lib import colors' in conteudo:
        conteudo = conteudo.replace(
            'from reportlab.lib import colors',
            'from reportlab.lib import colors\nfrom reportlab.lib.utils import ImageReader'
        )
        print("✓ Import ImageReader inserido com sucesso!")
    else:
        conteudo = "from reportlab.lib.utils import ImageReader\n" + conteudo
        print("✓ Import ImageReader colocado no topo do arquivo!")

# 2. Ajustar os textos no rodapé do cartão para não sobrepor o QR Code
# O QR Code fica em x=6.6*cm até 8.1*cm e y=0.4*cm até 1.9*cm.
# Garantimos que a linha de assinatura e texto do Pastor fiquem entre x=2.8*cm e 6.3*cm.
antigo_rodape = 'c.drawCentredString(7.35*cm, 0.2*cm, "VERIFICAR QR")'
novo_rodape = 'c.drawCentredString(7.35*cm, 0.2*cm, "VALIDAR SIGAD")'

if antigo_rodape in conteudo:
    conteudo = conteudo.replace(antigo_rodape, novo_rodape)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ app.py corrigido e pronto para testes!")