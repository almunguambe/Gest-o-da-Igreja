import os

dash_path = os.path.join("templates", "dashboard.html")

with open(dash_path, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Corrige a chamada de função que quebrava o Jinja2 com erro 500
conteudo = conteudo.replace("can_cadastro()", "pode_cadastro")

# 2. Garante que se o utilizador não tiver permissão de cadastro (ex: Tesoureiro), a aba ativa seja o dashboard
conteudo = conteudo.replace(
    '<section id="aba-membros" class="tab-content {% if pode_cadastro %}active{% endif %} space-y-6">',
    '<section id="aba-membros" class="tab-content {% if pode_cadastro %}active{% endif %} space-y-6">'
)
conteudo = conteudo.replace(
    '<section id="aba-dashboard" class="tab-content {% if not pode_cadastro and pode_tesouraria %}active{% endif %} space-y-6">',
    '<section id="aba-dashboard" class="tab-content {% if not pode_cadastro and pode_tesouraria %}active{% endif %} space-y-6">'
)

# 3. Garante que na Sidebar o item de menu também fique ativo corretamente no carregamento
conteudo = conteudo.replace(
    'id="nav-membros" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-black transition bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"',
    'id="nav-membros" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold transition {% if pode_cadastro %}bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black shadow-md{% else %}text-slate-300 hover:bg-white/10{% endif %}"'
)
conteudo = conteudo.replace(
    'id="nav-dashboard" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition"',
    'id="nav-dashboard" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold transition {% if not pode_cadastro and pode_tesouraria %}bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black shadow-md{% else %}text-slate-300 hover:bg-white/10{% endif %}"'
)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ templates/dashboard.html reparado com sucesso! A chamada inválida de função foi removida.")