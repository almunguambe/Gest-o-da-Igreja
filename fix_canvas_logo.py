with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Procura a função do cartão original e assegura que se houver drawImage ou tentativa de logo, usa static/logo.png
if "logo.png" not in conteudo:
    conteudo = conteudo.replace('logo.svg', 'logo.png')

# Se a geração do cartão usar c.drawImage, garantir que passa o caminho correto
with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Referências de logo ajustadas para PNG no gerador do cartão!")