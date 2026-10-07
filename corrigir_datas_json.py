with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Substituir a linha exata que causou o erro adicionando default=str
alvo = "json.dumps([dict(m) for m in todos_membros])"
novo = "json.dumps([dict(m) for m in todos_membros], default=str)"

if alvo in code:
    code = code.replace(alvo, novo)
    print("✓ Linha do json.dumps (membros) corrigida!")

# 2. Injetar uma configuração global para garantir que nenhum outro json.dumps falhe com datas
patch_global = """
import json
_original_dumps = json.dumps
def _custom_dumps(*args, **kwargs):
    if 'default' not in kwargs:
        kwargs['default'] = str
    return _original_dumps(*args, **kwargs)
json.dumps = _custom_dumps
"""

if "_custom_dumps" not in code:
    idx = code.find("app = Flask")
    if idx != -1:
        code = code[:idx] + patch_global.strip() + "\n\n" + code[idx:]
        print("✓ Serializador JSON global blindado para suportar datas do Postgres!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)