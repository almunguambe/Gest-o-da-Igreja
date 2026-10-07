with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Vamos localizar e remover exatamente o bloco residual entre o endif e o link do PDF
novo_conteudo = []
pular = False

for i, l in enumerate(linhas):
    # Se encontramos a linha com {% else %} órfão logo após {% if not tel_dir and not tel_preg %}
    if "{% else %}" in l and i > 1440 and i < 1470:
        pular = True
        continue
    if pular:
        if "{% endif %}" in l:
            pular = False
            continue
        continue
    novo_conteudo.append(l)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(novo_conteudo)

print("✓ Resíduo do Jinja2 removido com sucesso!")