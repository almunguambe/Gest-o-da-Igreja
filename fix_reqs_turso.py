conteudo = """flask
gunicorn
openpyxl
werkzeug
reportlab
pillow
libsql-experimental
"""
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✓ requirements.txt atualizado com libsql-experimental!")