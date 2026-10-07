import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Procura o nome do arquivo sqlite
dbs = set(re.findall(r'[\'"]([^\'"]+\.db)[\'"]', code))
print("Bancos SQLite encontrados:", list(dbs))

# Procura todas as instrucoes INSERT INTO membros
inserts = re.findall(r'INSERT INTO membros\s*\(([^)]+)\)', code, re.IGNORECASE)
print(f"\nForam encontrados {len(inserts)} comandos de INSERT na tabela membros.")
for i, inst in enumerate(inserts, 1):
    colunas_limpas = " ".join(inst.split())
    print(f"\n[INSERT #{i}]:\n({colunas_limpas})")