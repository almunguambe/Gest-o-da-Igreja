import os

# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM O BOTÃO NO MENU E O PAINEL DE NOTAS
dash_path = os.path.join("templates", "dashboard.html")
if os.path.exists(dash_path):
    with open(dash_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Adicionar botão de estudos no menu de navegação
    botao_menu_estudos = """                <a href="/estudos" class="tab-btn px-4 py-2 rounded-2xl transition flex items-center gap-1.5 bg-indigo-600/90 hover:bg-indigo-600 text-white font-extrabold shadow-sm">
                    <span>📖</span> <span>Área de Estudos (Manual)</span>
                </a>
                <button onclick="trocarAba('notas_alunos')" id="btn-notas_alunos" class="tab-btn px-4 py-2 rounded-2xl transition flex items-center gap-1.5 text-amber-300 hover:bg-white/10">
                    <span>🎓</span> <span>Notas dos Candidatos</span>
                </button>"""

    if "Área de Estudos (Manual)" not in html:
        html = html.replace("""<a href="/sistema/backup" class="tab-btn px-4 py-2 rounded-2xl transition flex items-center gap-1.5 bg-amber-600 text-white font-extrabold shadow-sm">
                    <span>💾</span> <span>Backup (.ZIP)</span>
                </a>""", """<a href="/sistema/backup" class="tab-btn px-4 py-2 rounded-2xl transition flex items-center gap-1.5 bg-amber-600 text-white font-extrabold shadow-sm">
                    <span>💾</span> <span>Backup (.ZIP)</span>
                </a>\n""" + botao_menu_estudos)

    # Adicionar a aba de notas dos candidatos
    aba_notas = """
        <!-- ================= ABA: NOTAS E PROGRESSO DOS CANDIDATOS ================= -->
        <section id="aba-notas_alunos" class="tab-content space-y-6">
            <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-6 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <div>
                        <h3 class="text-lg font-black text-slate-900">🎓 Acompanhamento dos Candidatos ao Batismo</h3>
                        <p class="text-xs text-slate-500 font-medium">Avaliações realizadas através do Manual de Integração e Batismo</p>
                    </div>
                    <a href="/estudos" class="h-10 px-4 bg-indigo-700 hover:bg-indigo-800 text-white font-black text-xs rounded-xl shadow flex items-center gap-1.5 transition">
                        <span>📖</span> <span>Entrar na Sala de Aula</span>
                    </a>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-gradient-to-r from-blue-900 to-indigo-950 text-white uppercase font-black">
                            <tr>
                                <th class="p-3">Data / Hora</th>
                                <th class="p-3">Candidato (Login)</th>
                                <th class="p-3">Lição Avaliada</th>
                                <th class="p-3 text-center">Aproveitamento</th>
                                <th class="p-3 text-center">Situação</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 bg-white">
                            {% if not lista_avaliacoes %}
                            <tr>
                                <td colspan="5" class="p-5 text-center text-slate-400 font-bold">
                                    Nenhum candidato concluiu testes ainda. Crie um utilizador com o perfil "Estudante" para os candidatos responderem às lições.
                                </td>
                            </tr>
                            {% endif %}
                            {% for av in lista_avaliacoes %}
                            <tr class="hover:bg-indigo-50/40">
                                <td class="p-3 text-slate-500 font-semibold">{{ av['data_resposta'] }}</td>
                                <td class="p-3 font-extrabold text-blue-950">{{ av['usuario'] }}</td>
                                <td class="p-3 font-bold text-slate-700">{{ av['licao'] }}</td>
                                <td class="p-3 text-center font-black text-sm text-indigo-900">{{ av['nota'] }}%</td>
                                <td class="p-3 text-center">
                                    {% if av['nota'] >= 70 %}
                                    <span class="bg-emerald-100 text-emerald-800 font-black px-2.5 py-1 rounded-full text-[11px]">Aprovado</span>
                                    {% else %}
                                    <span class="bg-amber-100 text-amber-800 font-black px-2.5 py-1 rounded-full text-[11px]">Reforçar Estudo</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    """

    if "aba-notas_alunos" not in html:
        html = html.replace("</main>", aba_notas + "\n    </main>")

    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ 1/2: templates/dashboard.html atualizado com botão e painel pastoral de notas!")

# 2. ATUALIZAR APP.PY PARA ENVIAR AS NOTAS DOS ALUNOS AO DASHBOARD E BOTÃO DE VOLTAR NO PORTAL DE ESTUDOS
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Passar lista_avaliacoes para o dashboard
if "lista_avaliacoes = conn.execute" not in app_code:
    app_code = app_code.replace("todos_membros = conn.execute", "lista_avaliacoes = conn.execute('SELECT * FROM avaliacoes_estudantes ORDER BY id DESC').fetchall()\n    todos_membros = conn.execute")
    app_code = app_code.replace("todos_membros=todos_membros,", "lista_avaliacoes=lista_avaliacoes,\n                           todos_membros=todos_membros,")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("✓ 2/2: app.py atualizado para sincronizar as notas com o painel pastoral!")

# 3. ATUALIZAR O TOPO DE TEMPLATES/ESTUDOS.HTML COM UM BOTÃO DE VOLTAR AO PAINEL CASO SEJA ADMIN
estudos_path = os.path.join("templates", "estudos.html")
if os.path.exists(estudos_path):
    with open(estudos_path, "r", encoding="utf-8") as f:
        html_estudos = f.read()
    
    botao_voltar = """            <div class="flex items-center space-x-2">
                {% if session.get('cargo') != 'Estudante' %}
                <a href="/" class="bg-blue-800 hover:bg-blue-700 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow transition">⬅ Voltar ao Painel</a>
                {% endif %}
                <span class="text-xs font-bold text-amber-300 bg-white/10 px-3 py-1.5 rounded-xl">{{ session['usuario'] }} ({{ session['cargo'] }})</span>
                <a href="/logout" class="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow transition">Sair</a>
            </div>"""

    if "Voltar ao Painel" not in html_estudos:
        html_estudos = html_estudos.replace("""            <div class="flex items-center space-x-2">
                <span class="text-xs font-bold text-amber-300 bg-white/10 px-3 py-1.5 rounded-xl">{{ session['usuario'] }} (Aluno)</span>
                <a href="/logout" class="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow transition">Sair</a>
            </div>""", botao_voltar)

    with open(estudos_path, "w", encoding="utf-8") as f:
        f.write(html_estudos)
    print("✓ templates/estudos.html atualizado com botão para o Pastor voltar ao painel principal!")