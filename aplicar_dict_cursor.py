with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Trocar qualquer import e uso de RealDictCursor por DictCursor
# DictCursor permite r[0] E r['nome'] ao mesmo tempo, exatamente como sqlite3.Row
if "RealDictCursor" in code:
    code = code.replace("RealDictCursor", "DictCursor")
    print("✓ Substituído RealDictCursor por DictCursor!")

# Ajustar wrapper ou conexoes diretas para garantir DictCursor
substituicoes = [
    ("cursor_factory=RealDictCursor", "cursor_factory=DictCursor"),
    ("from psycopg2.extras import RealDictCursor", "from psycopg2.extras import DictCursor")
]

for antigo, novo in substituicoes:
    if antigo in code:
        code = code.replace(antigo, novo)

# Garantir que a linha 421 ou consultas no dashboard não quebrem com ? no PostgreSQL
# Adaptar a função que executa a query se ela for um helper direto
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.py atualizado para suportar índices numéricos e nomes de colunas!")