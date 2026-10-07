with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Forçar status_inicial SEMPRE para 'Pendente de Validação' no /censo
antigo_status = "status_inicial = 'Ativo' if session.get('usuario') else 'Pendente de Validação'"
novo_status = "status_inicial = 'Pendente de Validação'"

if antigo_status in code:
    code = code.replace(antigo_status, novo_status)
    print("✓ Status do censo ajustado para SEMPRE exigir homologação!")

# 2. Garantir que a listagem de membros oficiais não puxe cadastros pendentes
# Substitui consultas diretas que não filtram status
substituicoes = [
    ("SELECT * FROM membros ORDER BY", "SELECT * FROM membros WHERE status = 'Ativo' OR status IS NULL ORDER BY"),
    ("SELECT id, nome, telefone, status FROM membros ORDER BY", "SELECT id, nome, telefone, status FROM membros WHERE status = 'Ativo' OR status IS NULL ORDER BY")
]

for de, para in substituicoes:
    if de in code and para not in code:
        code = code.replace(de, para)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Ajuste concluído com sucesso!")