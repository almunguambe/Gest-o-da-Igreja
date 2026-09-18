conteudo = """flask
gunicorn
openpyxl
werkzeug
reportlab
psycopg2-binary
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ requirements.txt atualizado com psycopg2-binary!")