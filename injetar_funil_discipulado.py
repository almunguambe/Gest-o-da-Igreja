with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

marcador = '    <!-- Tabela de Alunos e Progresso das Classes -->'

painel_funil = """    <!-- QUADRO RESUMO DO FUNIL DE DISCIPULADO -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
        <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4">
            <span class="text-xs font-bold text-amber-800 uppercase tracking-wider block">🌱 1. Novos Decididos</span>
            <p class="text-2xl font-black text-amber-900 mt-1">
                {{ membros | selectattr('fase_discipulado', 'equalto', 'Novo Decidido') | list | length }}
            </p>
            <span class="text-[11px] text-amber-700">Aguardando início de classes</span>
        </div>
        <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4">
            <span class="text-xs font-bold text-blue-800 uppercase tracking-wider block">📖 2. Em Discipulado</span>
            <p class="text-2xl font-black text-blue-900 mt-1">
                {{ membros | selectattr('fase_discipulado', 'equalto', 'Em Aulas / Classe') | list | length }}
            </p>
            <span class="text-[11px] text-blue-700">Estudando as lições doutrinárias</span>
        </div>
        <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4">
            <span class="text-xs font-bold text-emerald-800 uppercase tracking-wider block">🌊 3. Prontos p/ Batismo</span>
            <p class="text-2xl font-black text-emerald-900 mt-1">
                {{ membros | selectattr('fase_discipulado', 'equalto', 'Pronto para Batismo') | list | length }}
            </p>
            <span class="text-[11px] text-emerald-700">Aprovados para águas batismais</span>
        </div>
    </div>

    <!-- TABELA DE GESTÃO DIRETA DOS CANDIDATOS -->
    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 mb-6">
        <h4 class="text-xs font-black uppercase text-slate-700 mb-3 flex items-center justify-between">
            <span>Lista de Candidatos em Formação</span>
            <span class="text-[11px] font-semibold text-slate-500">Transição direta de fases</span>
        </h4>
        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs bg-white rounded-xl shadow-sm border border-slate-200">
                <thead class="bg-slate-100 text-slate-700 uppercase text-[10px] font-bold">
                    <tr>
                        <th class="p-2.5">Candidato</th>
                        <th class="p-2.5">Discipulador Responsável</th>
                        <th class="p-2.5">Fase Atual</th>
                        <th class="p-2.5 text-center">Avançar Fase</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for m in membros if m['fase_discipulado'] in ['Novo Decidido', 'Em Aulas / Classe', 'Pronto para Batismo'] %}
                    <tr>
                        <td class="p-2.5 font-bold text-slate-900">
                            {{ m['nome'] }}
                            <span class="block text-[10px] text-slate-400 font-normal">{{ m['telefone'] or 'Sem contato' }}</span>
                        </td>
                        <td class="p-2.5 text-slate-600 font-medium">
                            {{ m['discipulador'] or 'Não atribuído' }}
                        </td>
                        <td class="p-2.5">
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-black
                                {% if m['fase_discipulado'] == 'Novo Decidido' %}bg-amber-100 text-amber-800
                                {% elif m['fase_discipulado'] == 'Em Aulas / Classe' %}bg-blue-100 text-blue-800
                                {% else %}bg-emerald-100 text-emerald-800{% endif %}">
                                {{ m['fase_discipulado'] }}
                            </span>
                        </td>
                        <td class="p-2.5 text-center">
                            <form action="/discipulado/atualizar_fase" method="POST" class="inline-flex items-center gap-1.5">
                                <input type="hidden" name="membro_id" value="{{ m['id'] }}">
                                <select name="nova_fase" class="h-7 text-[11px] border rounded-lg px-1 bg-slate-50 font-bold">
                                    <option value="Em Aulas / Classe" {% if m['fase_discipulado'] == 'Em Aulas / Classe' %}selected{% endif %}>Em Aulas</option>
                                    <option value="Pronto para Batismo" {% if m['fase_discipulado'] == 'Pronto para Batismo' %}selected{% endif %}>Apto Batismo</option>
                                    <option value="Batizado">Batizado (Membro Efetivo)</option>
                                </select>
                                <button type="submit" class="h-7 px-2.5 bg-blue-900 hover:bg-blue-950 text-white font-bold text-[10px] rounded-lg shadow-sm transition">
                                    Salvar
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="p-4 text-center text-slate-400 text-xs italic">
                            Nenhum candidato em formação no momento. Registe um novo decidido ou altere a fase no cadastro de membros.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
"""

if marcador in conteudo and 'QUADRO RESUMO DO FUNIL DE DISCIPULADO' not in conteudo:
    conteudo = conteudo.replace(marcador, painel_funil + "\n" + marcador, 1)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Painel do funil de discipulado injetado com sucesso no dashboard.html!")
elif 'QUADRO RESUMO DO FUNIL DE DISCIPULADO' in conteudo:
    print("! O quadro de discipulado já está presente no template.")
else:
    print("! Marcador de inserção não encontrado.")