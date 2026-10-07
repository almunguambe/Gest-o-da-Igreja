with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Garantir o logotipo oficial logo.png
html = html.replace('logo.jpg', 'logo.png')

# 2. Tornar o cabeçalho dinâmico com o nome da congregação
html = html.replace('Chicuque • Gestão 360°', "{{ session.get('igreja_nome', 'IEAD Sede') }} • Gestão 360°")

# 3. Adicionar o atalho do SuperAdmin na barra lateral caso o utilizador tenha permissão
super_btn = """                    {% if session.get('is_superadmin') %}
                    <a href="/superadmin/igrejas" class="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl bg-indigo-600/90 text-white font-bold text-xs shadow-md hover:bg-indigo-600 transition">
                        <span class="text-base">🏛️</span>
                        <span>Gestão de Congregações</span>
                    </a>
                    {% endif %}
"""

if "/superadmin/igrejas" not in html:
    # Insere antes da lista de navegação
    ponto_insercao = '<div class="space-y-1">'
    if ponto_insercao in html:
        html = html.replace(ponto_insercao, ponto_insercao + '\n' + super_btn, 1)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Ajustes aplicados no template completo com sucesso!")