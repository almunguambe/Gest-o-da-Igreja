import os

dash_path = os.path.join("templates", "dashboard.html")

with open(dash_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Envolver a secção "Geral & Frequência" com a verificação correta para não deixar o título solto
antigo_bloco_geral = """                <!-- Secção Geral / Pastoral -->
                <div>
                    <span class="text-[10px] font-black uppercase tracking-wider text-indigo-400/80 px-3 block mb-1.5">Geral & Frequência</span>
                    <div class="space-y-1">
                        {% if pode_cadastro %}"""

novo_bloco_geral = """                <!-- Secção Geral / Pastoral -->
                {% if pode_cadastro %}
                <div>
                    <span class="text-[10px] font-black uppercase tracking-wider text-indigo-400/80 px-3 block mb-1.5">Geral & Frequência</span>
                    <div class="space-y-1">"""

if antigo_bloco_geral in html:
    html = html.replace(antigo_bloco_geral, novo_bloco_geral)
    html = html.replace("""                        {% endif %}
                    </div>
                </div>""", """                    </div>
                </div>
                {% endif %}""")

# 2. Ocultar o bloco "Doutrina & Batismo" de quem é apenas da Tesouraria
antigo_bloco_doutrina = """                <!-- Secção Educação & Discipulado -->
                <div>
                    <span class="text-[10px] font-black uppercase tracking-wider text-amber-400/80 px-3 block mb-1.5">Doutrina & Batismo</span>
                    <div class="space-y-1">
                        <a href="/estudos" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-extrabold text-amber-300 hover:bg-amber-950/40 transition">
                            <span class="text-base">📖</span> <span>Manual de Candidatos</span>
                        </a>
                        {% if e_admin or pode_cadastro %}
                        <button onclick="trocarAba('notas_alunos')" id="nav-notas_alunos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                            <span class="text-base">🎓</span> <span>Notas dos Alunos</span>
                        </button>
                        {% endif %}
                    </div>
                </div>"""

novo_bloco_doutrina = """                <!-- Secção Educação & Discipulado -->
                {% if pode_cadastro or e_admin %}
                <div>
                    <span class="text-[10px] font-black uppercase tracking-wider text-amber-400/80 px-3 block mb-1.5">Doutrina & Batismo</span>
                    <div class="space-y-1">
                        <a href="/estudos" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-extrabold text-amber-300 hover:bg-amber-950/40 transition">
                            <span class="text-base">📖</span> <span>Manual de Candidatos</span>
                        </a>
                        <button onclick="trocarAba('notas_alunos')" id="nav-notas_alunos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                            <span class="text-base">🎓</span> <span>Notas dos Alunos</span>
                        </button>
                    </div>
                </div>
                {% endif %}"""

if antigo_bloco_doutrina in html:
    html = html.replace(antigo_bloco_doutrina, novo_bloco_doutrina)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Permissões da Sidebar ajustadas com sucesso! A Tesouraria agora verá unicamente os menus financeiros.")