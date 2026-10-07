import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Encontra TODAS as ocorrências de palavras que começam com "can_" no código
todas_as_funcoes_can = set(re.findall(r'\b(can_[a-zA-Z0-9_]+)\b', code))
novas_funcoes = []

# 2. Para cada uma que encontrar, se não tiver sido definida ainda, cria automaticamente
for func in todas_as_funcoes_can:
    if f"def {func}(" not in code:
        novas_funcoes.append(f"""
def {func}():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    # Dá permissão geral aos cargos administrativos para o painel abrir
    return cargo in ['pastor', 'admin', 'superadmin', 'tesoureiro', 'tesouraria', 'secretário', 'secretaria', 'lider', 'líder']
""")

# 3. Injeta todas de uma vez no topo do ficheiro
if novas_funcoes:
    idx = code.find("app = Flask")
    if idx != -1:
        idx = code.find("\n", idx) + 1
        code = code[:idx] + "".join(novas_funcoes) + "\n\n" + code[idx:]
        print(f"✓ {len(novas_funcoes)} novas funções de permissão geradas automaticamente!")
else:
    print("✓ Todas as funções já estavam definidas.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)