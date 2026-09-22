with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Bloco visual refinado de estilo gala para o Discipulado
bloco_secao_gala = '''
<!-- ================= SEÇÃO DISCIPULADO & DOUTRINA BÍBLICA ================= -->
<div id="secao-discipulado" class="my-10 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
    <div class="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-100 gap-4">
        <div>
            <div class="flex items-center gap-2 mb-1">
                <span class="px-2.5 py-1 text-[11px] font-black uppercase tracking-wider bg-blue-50 text-blue-900 rounded-lg border border-blue-200">Escola de Líderes & Batismo</span>
                <span class="px-2.5 py-1 text-[11px] font-bold bg-amber-50 text-amber-900 rounded-lg border border-amber-200">Currículo Oficial IEAD</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900">🎓 Acompanhamento dos Candidatos & Discipulado</h2>
            <p class="text-xs sm:text-sm text-slate-500 mt-0.5">Gestão progressiva das 24 lições (Classes I a IV) e emissão de certificados oficiais</p>
        </div>
        <div class="flex items-center gap-2">
            <a href="/discipulado/classe/c1" target="_blank" class="px-4 py-2.5 bg-blue-900 hover:bg-blue-950 text-white font-bold text-xs rounded-xl shadow-sm transition inline-flex items-center gap-2">
                <span>📖</span> Abrir Manual dos Alunos
            </a>
        </div>
    </div>

    <!-- Tabela de Alunos e Progresso das Classes -->
    <div class="mt-6">
        <h3 class="text-sm font-extrabold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span>📊</span> Progresso de Formação por Classe
        </h3>
        <div class="overflow-x-auto rounded-2xl border border-slate-200">
            <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 text-slate-600 font-black border-b border-slate-200 uppercase tracking-wider">
                    <tr>
                        <th class="p-3.5">Candidato / Membro</th>
                        <th class="p-3.5 text-center">Classe I (Fundamentos)</th>
                        <th class="p-3.5 text-center">Classe II (Vida Cristã)</th>
                        <th class="p-3.5 text-center">Classe III (Maturidade)</th>
                        <th class="p-3.5 text-center">Classe IV (Batismo)</th>
                        <th class="p-3.5 text-center">Certificado Final</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 font-medium">
                    {% for ca in discipulado_alunos %}
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="p-3.5">
                            <div class="flex items-center gap-3">
                                {% if ca['foto_path'] %}
                                <img src="{{ ca['foto_path'] }}" class="w-8 h-8 rounded-full object-cover border border-slate-300">
                                {% else %}
                                <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-900 font-black flex items-center justify-center text-xs">
                                    {{ ca['nome'][:1] }}
                                </div>
                                {% endif %}
                                <div>
                                    <div class="font-bold text-slate-900">{{ ca['nome'] }}</div>
                                    <div class="text-[10px] text-slate-400">{{ ca['telefone'] or 'Sem contacto' }}</div>
                                </div>
                            </div>
                        </td>
                        <td class="p-3.5 text-center">
                            {% if ca['c1_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-black bg-emerald-100 text-emerald-800">Concluída ✓</span>
                            {% else %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-400">Em curso</span>
                            {% endif %}
                        </td>
                        <td class="p-3.5 text-center">
                            {% if ca['c2_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-black bg-emerald-100 text-emerald-800">Concluída ✓</span>
                            {% elif ca['c1_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800">Liberada</span>
                            {% else %}
                            <span class="text-slate-300 text-[10px] font-bold">Bloqueada 🔒</span>
                            {% endif %}
                        </td>
                        <td class="p-3.5 text-center">
                            {% if ca['c3_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-black bg-emerald-100 text-emerald-800">Concluída ✓</span>
                            {% elif ca['c2_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800">Liberada</span>
                            {% else %}
                            <span class="text-slate-300 text-[10px] font-bold">Bloqueada 🔒</span>
                            {% endif %}
                        </td>
                        <td class="p-3.5 text-center">
                            {% if ca['c4_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-black bg-emerald-100 text-emerald-800">Aprovado 🎓</span>
                            {% elif ca['c3_ok'] == 1 %}
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800">Liberada</span>
                            {% else %}
                            <span class="text-slate-300 text-[10px] font-bold">Bloqueada 🔒</span>
                            {% endif %}
                        </td>
                        <td class="p-3.5 text-center">
                            {% if ca['c4_ok'] == 1 %}
                            <a href="/membro/{{ ca['id'] }}/certificado_conclusao_discipulado" target="_blank" class="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-[11px] rounded-lg shadow-sm transition inline-flex items-center gap-1">
                                <span>📜</span> Emitir Certificado
                            </a>
                            {% else %}
                            <span class="text-[11px] text-slate-400 font-semibold">Pendente Classe IV</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="p-4 text-center text-slate-400">Nenhum membro matriculado no momento.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Seção de Dúvidas Bíblicas Associadas à Lição Específica -->
    <div class="mt-10 pt-8 border-t border-slate-100">
        <h3 class="text-sm font-extrabold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span>💬</span> Dúvidas Bíblicas dos Candidatos por Lição
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {% for d in duvidas %}
            <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between gap-2 mb-1.5">
                        <span class="font-bold text-xs text-blue-950">{{ d['membro_nome'] or 'Aluno' }}</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                            {{ d['licao_titulo'] or 'Lição Geral' }}
                        </span>
                    </div>
                    <div class="text-[11px] text-slate-500 mb-2 italic">Classe: {{ d['classe_nome'] or 'Discipulado' }}</div>
                    <div class="text-xs text-slate-700 bg-white p-3 rounded-xl border border-slate-200 leading-relaxed font-medium">
                        "{{ d['duvida'] }}"
                    </div>
                </div>

                <div class="mt-3 pt-3 border-t border-slate-200/60">
                    {% if d['resposta'] %}
                    <div class="bg-emerald-50 border border-emerald-200 p-2.5 rounded-xl">
                        <span class="text-[10px] font-black uppercase text-emerald-800 block mb-0.5">Resposta Pastoral Enviada:</span>
                        <p class="text-xs text-emerald-950">{{ d['resposta'] }}</p>
                    </div>
                    {% else %}
                    <form action="/discipulado/responder_duvida/{{ d['id'] }}" method="POST" class="flex gap-2">
                        <input type="text" name="resposta" placeholder="Escreva a resposta bíblica para o aluno..." class="flex-1 px-3 py-1.5 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900" required>
                        <button type="submit" class="px-3 py-1.5 bg-blue-900 text-white font-bold text-xs rounded-xl hover:bg-blue-950 transition">
                            Responder
                        </button>
                    </form>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="col-span-full p-6 text-center bg-slate-50 border border-dashed border-slate-200 rounded-2xl text-slate-400 text-xs">
                Nenhuma dúvida pendente. Quando os alunos enviarem perguntas durante os estudos, elas aparecerão aqui organizadas pela lição exata.
            </div>
            {% endfor %}
        </div>
    </div>
</div>
'''

# Substitui o bloco antigo de acompanhamento no dashboard pelo bloco refinado
if "Acompanhamento dos Candidatos ao Batismo" in html or "Dúvidas Bíblicas dos Candidatos" in html:
    partes = html.split('<h3 class="text-lg font-black text-slate-900">🎓 Acompanhamento dos Candidatos ao Batismo</h3>')
    if len(partes) > 1:
        inicio = partes[0].rsplit('<div', 1)[0]
        # Pega o fim da seção anterior
        resto = partes[1].split('</section>', 1)
        if len(resto) > 1:
            html = inicio + bloco_secao_gala + '</section>' + resto[1]
        else:
            resto_div = partes[1].split('</div>\n        </div>', 1)
            html = inicio + bloco_secao_gala + resto_div[-1]

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ templates/dashboard.html atualizado com layout de gala e gestão de dúvidas!")