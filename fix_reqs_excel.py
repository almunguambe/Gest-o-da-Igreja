conteudo = """Flask==3.0.3
gunicorn==22.0.0
reportlab==4.2.2
pillow==10.4.0
openpyxl==3.1.5
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ requirements.txt atualizado com openpyxl!")