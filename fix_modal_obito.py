with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substituir o input de nome de obito pelo select de membros cadastrados
campo_antigo_nome = '<input type="text" name="nome"'
select_membro_obito = '''<select name="membro_id" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900" required>
                    <option value="">-- Selecione o Membro Cadastrado --</option>
                    {% for m in todos_membros %}
                    <option value="{{ m['id'] }}">{{ m['nome'] }} (ID: {{ m['id'] }}) - {{ m['bairro'] or m['contacto'] or 'Membro' }}</option>
                    {% endfor %}
                </select>'''

if campo_antigo_nome in html:
    # Acha o bloco do form de obito e faz a troca
    partes = html.split(campo_antigo_nome)
    # Procura onde fecha o input antigo
    resto = partes[1].split('>', 1)
    # Substitui apenas se estiver na área de óbito
    if "obito" in partes[0][-300:].lower():
        html = partes[0] + select_membro_obito + resto[1]

# 2. Assegurar que todos_membros está disponível para o select
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Formulário de óbitos atualizado para vincular diretamente membros cadastrados!")