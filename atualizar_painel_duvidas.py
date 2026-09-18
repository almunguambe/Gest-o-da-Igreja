import os

dash_path = os.path.join("templates", "dashboard.html")

with open(dash_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Adicionar o item na Sidebar
antigo_menu_alunos = """                        <button onclick="trocarAba('notas_alunos')" id="nav-notas_alunos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                            <span class="text-base">🎓</span> <span>Notas dos Alunos</span>
                        </button>"""

novo_menu_alunos = """                        <button onclick="trocarAba('notas_alunos')" id="nav-notas_alunos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                            <span class="text-base">🎓</span> <span>Notas dos Alunos</span>
                        </button>
                        <button onclick="trocarAba('duvidas_alunos')" id="nav-duvidas_alunos" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-bold text-slate-300 hover:bg-white/10 transition">
                            <span class="text-base">💬</span> <span>Dúvidas dos Alunos</span>
                        </button>"""

if antigo_menu_alunos in html and "nav-duvidas_alunos" not in html:
    html = html.replace(antigo_menu_alunos, novo_menu_alunos)

# 2. Adicionar a Seção/Aba de Dúvidas dos Alunos
secao_duvidas_pastor = """
            <!-- ================= ABA: DÚVIDAS DOS ALUNOS (RESPOSTA PASTORAL) ================= -->
            <section id="aba-duvidas_alunos" class="tab-content space-y-6">
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-6 space-y-4">
                    <div class="border-b pb-3 flex justify-between items-center">
                        <div>
                            <h3 class="text-lg font-black text-slate-900 flex items-center gap-2">
                                <span>💬</span> <span>Dúvidas Bíblicas dos Candidatos ao Batismo</span>
                            </h3>
                            <p class="text-xs text-slate-500 font-medium">Responda diretamente aos alunos para que a orientação apareça na sala de aula virtual deles</p>
                        </div>
                    </div>

                    <div class="space-y-4">
                        {% if not todas_duvidas %}
                        <div class="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200 text-slate-400 font-bold text-xs">
                            Nenhum candidato enviou dúvidas no sistema até ao momento.
                        </div>
                        {% endif %}

                        {% for d in todas_duvidas %}
                        <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="text-xs font-black text-blue-900 bg-blue-100 px-2.5 py-0.5 rounded-full">{{ d['usuario'] }}</span>
                                    <span class="text-xs font-bold text-slate-500 ml-2">Lição: {{ d['licao'] }}</span>
                                    <span class="text-[11px] text-slate-400 ml-2">• {{ d['data_envio'] }}</span>
                                </div>
                                <div>
                                    {% if d['resposta'] %}
                                    <span class="bg-emerald-100 text-emerald-800 text-[11px] font-black px-2.5 py-0.5 rounded-full">Respondida</span>
                                    {% else %}
                                    <span class="bg-amber-100 text-amber-800 text-[11px] font-black px-2.5 py-0.5 rounded-full animate-pulse">Pendente</span>
                                    {% endif %}
                                </div>
                            </div>

                            <div class="p-3 bg-white rounded-xl border text-xs font-semibold text-slate-800">
                                <strong>Pergunta do Aluno:</strong> {{ d['duvida'] }}
                            </div>

                            {% if d['resposta'] %}
                            <div class="p-3 bg-emerald-50/70 border border-emerald-200 rounded-xl text-xs text-emerald-950">
                                <strong>Resposta Pastoral Registada:</strong>
                                <p class="mt-1 font-medium whitespace-pre-line">{{ d['resposta'] }}</p>
                            </div>
                            {% endif %}

                            <!-- Formulário para Responder ou Atualizar Resposta -->
                            <form action="/estudos/duvidas/responder/{{ d['id'] }}" method="POST" class="space-y-2 pt-1">
                                <label class="block text-[11px] font-bold text-slate-600">
                                    {% if d['resposta'] %}Atualizar Resposta:{% else %}Escrever Resposta Pastoral:{% endif %}
                                </label>
                                <div class="flex gap-2">
                                    <textarea name="resposta" rows="2" required placeholder="Digite a explicação bíblica para o aluno..." class="w-full p-2.5 text-xs border rounded-xl outline-none focus:border-blue-600 bg-white font-medium">{{ d['resposta'] or '' }}</textarea>
                                    <button type="submit" class="px-4 bg-indigo-900 hover:bg-indigo-950 text-white font-black text-xs rounded-xl shadow whitespace-nowrap transition flex items-center justify-center">
                                        Enviar
                                    </button>
                                </div>
                            </form>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </section>
"""

if "aba-duvidas_alunos" not in html:
    html = html.replace("</main>", secao_duvidas_pastor + "\n        </main>")

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✓ templates/dashboard.html atualizado com o painel pastoral de respostas!")