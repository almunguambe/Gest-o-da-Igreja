import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Procura chamadas de funções que comecem por 'can_', 'is_', ou 'has_' seguidas de parênteses
todas_funcoes = set(re.findall(r'\b(can_[a-zA-Z0-9_]+|is_[a-zA-Z0-9_]+|has_[a-zA-Z0-9_]+)\s*\(', code))
novas_funcoes = []

for func in todas_funcoes:
    # Se a função ainda não existir no código, cria-a
    if f"def {func}(" not in code:
        novas_funcoes.append(f"""
def {func}():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'superadmin', 'tesoureiro', 'tesouraria', 'secretário', 'secretaria', 'lider', 'líder']
""")

if novas_funcoes:
    idx = code.find("app = Flask")
    if idx != -1:
        # Insere logo a seguir à inicialização do Flask
        idx = code.find("\n", idx) + 1
        code = code[:idx] + "".join(novas_funcoes) + "\n\n" + code[idx:]
        print(f"✓ {len(novas_funcoes)} funções de segurança geradas (is_*, can_*, has_*)!")
else:
    print("✓ Nenhuma função em falta encontrada.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)