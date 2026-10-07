with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Remover qualquer botão antigo de switchTab que tenha ficado
conteudo = re.sub(r'<button\s+onclick="switchTab\(\'aba-secretaria\'\)".*?</button>\s*', '', conteudo, flags=re.DOTALL)

# 2. Inserir o botão nativo do menu com trocarAba('secretaria')
botao_menu_secretaria = '''
                         <button onclick="trocarAba('secretaria')" id="nav-secretaria" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                             <span class="text-base">📋</span> <span>Secretaria & Planos</span>
                         </button>
'''

# Se o botão ainda não estiver com a chamada trocarAba('secretaria'), injeta logo após nav-cultos
if "trocarAba('secretaria')" not in conteudo:
    alvo_cultos = '''<button onclick="trocarAba('cultos')" id="nav-cultos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                             <span class="text-base">⛪</span> <span>Cultos & Presenças</span>
                         </button>'''
    if alvo_cultos in conteudo:
        conteudo = conteudo.replace(alvo_cultos, alvo_cultos + botao_menu_secretaria)
    else:
        # Fallback por regex
        conteudo = re.sub(r'(<button\s+onclick="trocarAba\(\'cultos\'\)".*?</button>)', r'\1' + botao_menu_secretaria, conteudo, count=1, flags=re.DOTALL)
    print("✓ Botão Secretaria inserido no menu lateral com trocarAba!")

# 3. Garantir que a section #aba-secretaria use o padrão de classes .tab-content
conteudo = conteudo.replace('<section id="aba-secretaria" class="tab-content hidden space-y-6">', '<section id="aba-secretaria" class="tab-content space-y-6">')

# 4. Assegurar regra CSS de abas ativas caso falte
css_active = """
<style>
.tab-content { display: none; }
.tab-content.active { display: block; }
</style>
"""
if '.tab-content.active' not in conteudo:
    conteudo = conteudo.replace('</head>', css_active + '\n</head>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html perfeitamente alinhado com o sistema!")