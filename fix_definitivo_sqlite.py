# 1. Limpar requirements.txt (apenas o que funciona sem erro)
reqs = """Flask==3.0.3
gunicorn==22.0.0
reportlab==4.2.2
pillow==10.4.0
"""
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(reqs)

# 2. Configurar o app.py para gravar na pasta persistente se ela existir
with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Remover qualquer vestígio de psycopg2/DATABASE_URL que quebra o build
linhas = conteudo.splitlines()
novas = []
pulando = False
for l in linhas:
    if "import psycopg2" in l or "DATABASE_URL =" in l:
        continue
    novas.append(l)

conteudo = "\n".join(novas)

# Definir caminho do banco: se houver pasta /var/data usa ela, senão usa local
banco_config = '''import os
DATA_DIR = "/var/data" if os.path.exists("/var/data") else "."
DB_NAME = os.path.join(DATA_DIR, "gestao_chicuque.db")
'''

if "DB_NAME =" in conteudo:
    partes = conteudo.split("DB_NAME =")
    # pega o resto após a quebra de linha
    resto = partes[1].split("\n", 1)[1]
    conteudo = partes[0] + banco_config + resto

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Sistema restaurado para SQLite puro e leve!")