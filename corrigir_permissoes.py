with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Bloco de funções de permissão baseadas no cargo da sessão
helpers_permissoes = """
def can_cadastro():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'secretário', 'secretaria', 'secretario', 'tesoureiro', 'tesouraria', 'superadmin']

def can_financeiro():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'tesoureiro', 'tesouraria', 'superadmin']

def can_admin():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'superadmin']
"""

if "def can_cadastro" not in code:
    # Inserir logo no início, após a inicialização do Flask
    idx = code.find("app = Flask")
    if idx != -1:
        idx = code.find("\n", idx) + 1
        code = code[:idx] + "\n" + helpers_permissoes.strip() + "\n\n" + code[idx:]
        print("✓ Funções de permissão (can_cadastro, can_financeiro, can_admin) adicionadas!")
else:
    print("✓ As funções de permissão já existem.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)