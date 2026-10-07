with open('templates/login.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Substituir o ícone genérico de livro pelo logotipo oficial
icone_livro = """            <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-tr from-blue-900 to-indigo-700 text-white rounded-3xl shadow-xl shadow-blue-950/20 mb-3 ring-4 ring-white">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            </div>"""

logo_oficial = """            <div class="inline-flex items-center justify-center w-24 h-24 bg-white rounded-3xl shadow-xl p-2 mb-3 ring-4 ring-indigo-50">
                <img src="/static/logo.png" alt="IEAD" class="w-full h-full object-contain">
            </div>"""

if icone_livro in html:
    html = html.replace(icone_livro, logo_oficial)
    print("✓ Logótipo oficial inserido no login!")

# 2. Atualizar títulos do sistema-mãe
html = html.replace("Congregação de Chicuque", "Assembleia de Deus")
html = html.replace("Sistema de Gestão & Tesouraria Eclesiástica", "Portal Integrado de Gestão Multi-Congregações")
html = html.replace("IEAD Chicuque", "IEAD Moçambique")

with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Tela de login atualizada para o Sistema-Mãe com sucesso!")