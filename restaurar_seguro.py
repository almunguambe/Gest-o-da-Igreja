with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Garante apenas que o botão Secretaria use trocarAba('secretaria')
botao_secretaria = '''
                         <button onclick="trocarAba('secretaria')" id="nav-secretaria" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                             <span class="text-base">📋</span> <span>Secretaria & Planos</span>
                         </button>'''

if "trocarAba('secretaria')" not in conteudo:
    alvo = '<button onclick="trocarAba(\'cultos\')"'
    conteudo = conteudo.replace(alvo, botao_secretaria + '\n                         ' + alvo)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Restaurado com segurança sem alterar nenhum formulário!")