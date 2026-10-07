with open('templates/login.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Atualizar o título da página no navegador
html = html.replace("<title>IEAD Moçambique - Portal Administrativo</title>", "<title>SIGAD • Sistema Integrado de Gestão da Assembleia de Deus</title>")

# 2. Bloco do cabeçalho antigo
bloco_antigo = """            <!-- Logótipo e Cabeçalho -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-24 h-24 mb-4 rounded-2xl bg-gradient-to-tr from-blue-950 via-blue-900 to-indigo-800 p-2 shadow-xl ring-4 ring-blue-50 relative group">
                    <!-- Imagem oficial da Logo -->
                    <img src="/static/logo.svg?v=iead2026" alt="Logo IEAD" class="w-full h-full object-contain rounded-xl" onerror="this.style.display='none'; document.getElementById('emblema-padrao').style.display='flex';">
                    
                    <!-- Emblema de recurso (SVG da Bíblia e Cruz) caso logo.png não exista ainda -->
                    <div id="emblema-padrao" style="display:none;" class="w-full h-full items-center justify-center text-amber-300">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                    </div>
                </div>

                <span class="inline-block text-[11px] font-bold uppercase tracking-widest text-blue-800 bg-blue-50 px-3 py-1 rounded-full border border-blue-100 mb-2">
                    Assembleia de Deus
                </span>
                <h1 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-tight">
                    Assembleia de Deus
                </h1>
                <p class="text-xs font-medium text-slate-500 mt-1">
                    Portal Integrado de Gestão Multi-Congregações
                </p>
            </div>"""

# 3. Novo cabeçalho oficial com logo.png e identidade SIGAD
bloco_novo = """            <!-- Logótipo e Cabeçalho Oficial SIGAD -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-24 h-24 mb-4 rounded-3xl bg-white p-2.5 shadow-xl ring-4 ring-indigo-50/80">
                    <img src="{{ url_for('static', filename='logo.png') }}" alt="IEAD Oficial" class="w-full h-full object-contain">
                </div>

                <div>
                    <span class="inline-block text-[10px] font-black uppercase tracking-widest text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100 mb-2">
                        Assembleia de Deus
                    </span>
                    <h1 class="text-3xl font-black tracking-tight text-slate-900 font-sans">
                        SIGAD
                    </h1>
                    <p class="text-xs font-semibold text-slate-500 mt-1">
                        Sistema Integrado de Gestão Eclesiástica
                    </p>
                </div>
            </div>"""

if bloco_antigo in html:
    html = html.replace(bloco_antigo, bloco_novo)
    print("✓ Cabeçalho SIGAD e logo.png aplicados com sucesso!")
else:
    print("! Bloco exato não encontrado, aplicando substituições diretas...")
    html = html.replace('/static/logo.svg?v=iead2026', "{{ url_for('static', filename='logo.png') }}")
    html = html.replace('alt="Logo IEAD" class="w-full h-full object-contain rounded-xl" onerror="this.style.display=\'none\'; document.getElementById(\'emblema-padrao\').style.display=\'flex\';"', 'alt="Logo IEAD" class="w-full h-full object-contain rounded-xl"')
    html = html.replace('<h1 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-tight">\n                    Assembleia de Deus\n                </h1>', '<h1 class="text-3xl font-black tracking-tight text-slate-900 font-sans">\n                    SIGAD\n                </h1>')
    html = html.replace('Portal Integrado de Gestão Multi-Congregações', 'Sistema Integrado de Gestão Eclesiástica')

with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Ficheiro templates/login.html atualizado!")