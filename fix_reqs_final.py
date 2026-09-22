conteudo = """Flask==3.0.3
gunicorn==22.0.0
reportlab==4.2.2
pillow==10.4.0
openpyxl==3.1.5
psycopg2-binary==2.9.9
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ requirements.txt pronto com openpyxl e psycopg2-binary!")