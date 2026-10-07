with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Adicionar o item no menu lateral se ainda não tiver
menu_item = '''
            <button onclick="switchTab('aba-secretaria')" class="tab-btn w-full flex items-center space-x-3 px-4 py-3 rounded-2xl text-white/70 hover:text-white hover:bg-white/10 transition-all font-bold text-xs">
                <span>📋</span>
                <span>Secretaria & Planos</span>
            </button>
'''

if 'aba-secretaria' not in conteudo:
    # Insere logo abaixo de Membros ou Cultos no menu lateral
    conteudo = conteudo.replace('<button onclick="switchTab(\'aba-cultos\')"', menu_item + '\n            <button onclick="switchTab(\'aba-cultos\')"')
    print("✓ Botão Secretaria adicionado no menu lateral!")

# 2. Adicionar o corpo da aba secretaria
corpo_secretaria = '''
            <!-- ================= ABA SECRETARIA & PLANIFICAÇÃO ================= -->
            <section id="aba-secretaria" class="tab-content hidden space-y-6">
                <!-- Cabeçalho com Acesso ao Relatório Oficial -->
                <div class="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-xl font-black">📋 Secretaria Geral & Planificação de Actividades</h2>
                        <p class="text-xs text-blue-200 mt-1">Conforme o Modelo Oficial de Relatório da Assembleia de Deus (Ministério Thavane)</p>
                    </div>
                    <div class="flex gap-2">
                        <a href="/secretaria/relatorio_oficial" target="_blank" class="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs rounded-xl shadow transition flex items-center gap-2">
                            <span>📄</span> Visualizar / Imprimir Relatório Oficial
                        </a>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    <!-- Formulário de Planificação -->
                    <div class="lg:col-span-4 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5">
                        <h3 class="text-base font-black text-slate-900 mb-3 pb-2 border-b">📌 Planificar Nova Actividade</h3>
                        <form action="/secretaria/planificacao/nova" method="POST" class="space-y-3">
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Departamento</label>
                                <select name="departamento" required class="w-full h-10 px-2 text-xs border-2 rounded-xl bg-white font-bold">
                                    <option value="Activista Cristã">Activista Cristã</option>
                                    <option value="Juventude Cristã">Juventude Cristã</option>
                                    <option value="Boa Esperança (Adolescentes e Crianças)">Boa Esperança</option>
                                    <option value="Depart. dos Pais">Depart. dos Pais</option>
                                    <option value="Depart. das Mães">Depart. das Mães</option>
                                    <option value="Escola Dominical">Escola Dominical</option>
                                    <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                                    <option value="Conselho Pastoral / Obreiros">Conselho Pastoral / Obreiros</option>
                                    <option value="Geral da Igreja">Geral da Igreja</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Tipo de Evento</label>
                                <select name="tipo_evento" class="w-full h-10 px-2 text-xs border-2 rounded-xl bg-white">
                                    <option value="Seminário">Seminário</option>
                                    <option value="Conferência">Conferência</option>
                                    <option value="Evangelização / Cruzada">Evangelização / Cruzada</option>
                                    <option value="Retiro Espiritual">Retiro Espiritual</option>
                                    <option value="Aniversário de Departamento">Aniversário de Departamento</option>
                                    <option value="Reunião Geral">Reunião Geral</option>
                                    <option value="Outro">Outro</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Nome da Actividade</label>
                                <input type="text" name="actividade" required placeholder="Ex: Seminário de Liderança Juvenil" class="w-full h-10 px-3 text-xs border-2 rounded-xl">
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="text-[11px] font-bold text-slate-600 block mb-1">Data Prevista</label>
                                    <input type="date" name="data_prevista" required class="w-full h-10 px-2 text-xs border-2 rounded-xl">
                                </div>
                                <div>
                                    <label class="text-[11px] font-bold text-slate-600 block mb-1">Frequência</label>
                                    <select name="frequencia" class="w-full h-10 px-2 text-xs border-2 rounded-xl bg-white">
                                        <option value="Pontual">Pontual / Única</option>
                                        <option value="Semanal">Semanal</option>
                                        <option value="Mensal">Mensal</option>
                                        <option value="Trimestral">Trimestral</option>
                                        <option value="Anual">Anual</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Responsável Directo</label>
                                <input type="text" name="responsavel" required placeholder="Nome do Irmão/Obreiro" class="w-full h-10 px-3 text-xs border-2 rounded-xl">
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Contacto / WhatsApp (para Notificação)</label>
                                <input type="text" name="contacto_responsavel" placeholder="Ex: 841234567" class="w-full h-10 px-3 text-xs border-2 rounded-xl">
                            </div>
                            <button type="submit" class="w-full h-11 bg-indigo-900 hover:bg-indigo-800 text-white font-black text-xs rounded-xl shadow transition">Gravar Planificação</button>
                        </form>
                    </div>

                    <!-- Lista de Monitoramento das Actividades -->
                    <div class="lg:col-span-8 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 space-y-4">
                        <h3 class="text-base font-black text-slate-900 pb-2 border-b">📊 Monitoramento do Cronograma Eclesiástico</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-50 border-b text-slate-600 font-bold">
                                    <tr>
                                        <th class="p-2.5">Actividade / Depto</th>
                                        <th class="p-2.5">Data Prevista</th>
                                        <th class="p-2.5">Responsável & Contacto</th>
                                        <th class="p-2.5 text-center">Status</th>
                                        <th class="p-2.5 text-center">Ações</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    {% for p in planos %}
                                    <tr class="hover:bg-slate-50/60">
                                        <td class="p-2.5 font-semibold text-slate-800">
                                            <div class="font-bold text-slate-900">{{ p['actividade'] }}</div>
                                            <div class="text-[10px] text-indigo-700 font-semibold">{{ p['departamento'] }} • {{ p['tipo_evento'] }}</div>
                                        </td>
                                        <td class="p-2.5 whitespace-nowrap">{{ p['data_prevista'] }}</td>
                                        <td class="p-2.5">
                                            <div>{{ p['responsavel'] }}</div>
                                            {% if p['contacto_responsavel'] %}
                                            <a href="https://wa.me/258{{ p['contacto_responsavel']|replace(' ', '')|replace('+', '') }}?text=Paz%20do%20Senhor%20Irmão(a)%20{{ p['responsavel'] }},%20lembrete%20sobre%20a%20actividade:%20{{ p['actividade'] }}" target="_blank" class="inline-flex items-center gap-1 text-[10px] text-emerald-700 font-bold hover:underline">
                                                <span>📲 WhatsApp</span>
                                            </a>
                                            {% endif %}
                                        </td>
                                        <td class="p-2.5 text-center">
                                            {% if p['status'] == 'Realizado' %}
                                                <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">✓ Realizado</span>
                                            {% elif p['status'] == 'Em Andamento' %}
                                                <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-100 text-amber-800">⏳ Em Andamento</span>
                                            {% elif p['status'] == 'Cancelado' %}
                                                <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-100 text-rose-800">✕ Cancelado</span>
                                            {% else %}
                                                <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-blue-100 text-blue-800">📅 Planeado</span>
                                            {% endif %}
                                        </td>
                                        <td class="p-2.5 text-center">
                                            <button onclick="abrirModalRelatar({{ p['id'] }}, '{{ p['actividade'] }}', '{{ p['tipo_evento'] }}')" class="px-3 py-1 bg-slate-900 hover:bg-indigo-900 text-white font-bold text-[10px] rounded-lg shadow">
                                                📝 Relatar
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="5" class="p-6 text-center text-slate-400">Nenhuma actividade planificada ainda. Cadastre a primeira ao lado.</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- MODAL DINÂMICO PARA RELATAR ACTIVIDADE -->
            <div id="modal-relatar" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
                <div class="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
                    <div class="flex justify-between items-center border-b pb-3">
                        <h3 class="font-black text-slate-900 text-base" id="modal-titulo-actividade">Relatório de Execução</h3>
                        <button onclick="fecharModalRelatar()" class="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
                    </div>

                    <form id="form-modal-relatar" action="" method="POST" class="space-y-4">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Status Actual</label>
                                <select name="status" class="w-full h-10 px-2 text-xs border-2 rounded-xl bg-white font-bold">
                                    <option value="Realizado">Realizado</option>
                                    <option value="Em Andamento">Em Andamento</option>
                                    <option value="Cancelado">Cancelado</option>
                                    <option value="Adiado">Adiado</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">Data da Realização</label>
                                <input type="date" name="data_realizacao" class="w-full h-10 px-2 text-xs border-2 rounded-xl">
                            </div>
                        </div>

                        <!-- Participação Discriminada -->
                        <div class="p-3 bg-slate-50 border rounded-2xl space-y-2">
                            <span class="text-[11px] font-black uppercase tracking-wider text-slate-700 block">👥 Participantes no Evento (Discriminado)</span>
                            <div class="grid grid-cols-4 gap-2">
                                <div>
                                    <label class="text-[10px] font-semibold text-slate-600 block">Homens</label>
                                    <input type="number" min="0" name="homens_participantes" value="0" class="w-full h-9 px-1 text-xs border-2 rounded-lg text-center font-bold">
                                </div>
                                <div>
                                    <label class="text-[10px] font-semibold text-slate-600 block">Mulheres</label>
                                    <input type="number" min="0" name="mulheres_participantes" value="0" class="w-full h-9 px-1 text-xs border-2 rounded-lg text-center font-bold">
                                </div>
                                <div>
                                    <label class="text-[10px] font-semibold text-slate-600 block">Jovens</label>
                                    <input type="number" min="0" name="jovens_participantes" value="0" class="w-full h-9 px-1 text-xs border-2 rounded-lg text-center font-bold">
                                </div>
                                <div>
                                    <label class="text-[10px] font-semibold text-slate-600 block">Crianças</label>
                                    <input type="number" min="0" name="criancas_participantes" value="0" class="w-full h-9 px-1 text-xs border-2 rounded-lg text-center font-bold">
                                </div>
                            </div>
                        </div>

                        <!-- Para Seminários e Retiros: Temas Abordados -->
                        <div>
                            <label class="text-[11px] font-bold text-slate-600 block mb-1">📖 Temas Abordados / Ministrações (Crucial para Relatório Thavane)</label>
                            <textarea name="temas_abordados" rows="2" placeholder="Ex: Tema: Fidelidade no Lar; Preletor: Ev. Romão..." class="w-full p-2.5 text-xs border-2 rounded-xl"></textarea>
                        </div>

                        <!-- Para Evangelismo: Pessoas Alcançadas & Decisões -->
                        <div class="grid grid-cols-2 gap-2 p-3 bg-emerald-50/70 border border-emerald-200 rounded-2xl">
                            <div>
                                <label class="text-[10px] font-black text-emerald-950 block">📢 Pessoas Alcançadas</label>
                                <input type="number" min="0" name="pessoas_alcancadas" value="0" class="w-full h-9 px-2 text-xs border-2 border-emerald-300 rounded-lg text-center font-bold bg-white">
                            </div>
                            <div>
                                <label class="text-[10px] font-black text-emerald-950 block">✝️ Tomaram Decisão / Conversões</label>
                                <input type="number" min="0" name="decisoes_convertidos" value="0" class="w-full h-9 px-2 text-xs border-2 border-emerald-300 rounded-lg text-center font-bold bg-white">
                            </div>
                        </div>

                        <div>
                            <label class="text-[11px] font-bold text-slate-600 block mb-1">Notas / Dificuldades / Observações</label>
                            <textarea name="relatorio_observacoes" rows="2" placeholder="Dificuldades enfrentadas, constrangimentos..." class="w-full p-2.5 text-xs border-2 rounded-xl"></textarea>
                        </div>

                        <div class="flex justify-end gap-2 pt-2">
                            <button type="button" onclick="fecharModalRelatar()" class="px-4 py-2 border rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
                            <button type="submit" class="px-5 py-2 bg-blue-900 hover:bg-blue-800 text-white rounded-xl text-xs font-black shadow">Salvar Relatório da Actividade</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
            function abrirModalRelatar(id, actividade, tipo) {
                document.getElementById('modal-titulo-actividade').innerText = 'Relatar Actividade: ' + actividade + ' (' + tipo + ')';
                document.getElementById('form-modal-relatar').action = '/secretaria/planificacao/relatar/' + id;
                document.getElementById('modal-relatar').classList.remove('hidden');
            }
            function fecharModalRelatar() {
                document.getElementById('modal-relatar').classList.add('hidden');
            }
            </script>
'''

if 'id="aba-secretaria"' not in conteudo:
    # Insere antes do fechamento da tag main ou antes de outra aba
    conteudo = conteudo.replace('<!-- ================= ABA 2: CULTOS ================= -->', corpo_secretaria + '\n\n            <!-- ================= ABA 2: CULTOS ================= -->')
    print("✓ Aba de Secretaria e Planificação inserida com sucesso no dashboard.html!")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)