import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Atualizar o cabeçalho da tabela de escalas para incluir o cabeçalho de Notificação
cabecalho_antigo = '<thead class="bg-slate-50 border-b"><tr><th class="p-2.5">Data/Culto</th><th class="p-2.5">Pregador</th><th class="p-2.5 text-center">PDF</th></tr></thead>'
cabecalho_novo = '<thead class="bg-slate-50 border-b"><tr><th class="p-2.5">Data/Culto</th><th class="p-2.5">Pregador</th><th class="p-2.5 text-center">Status / Lembrete</th><th class="p-2.5 text-center">Ações</th></tr></thead>'

if cabecalho_antigo in html:
    html = html.replace(cabecalho_antigo, cabecalho_novo)
    print("✓ Cabeçalho da tabela de escalas atualizado!")

# 2. Substituir a linha do loop de escalas com o botão dinâmico do WhatsApp e cálculo de dias
linha_loop_antiga = """                                <tr>
                                    <td class="p-2.5 font-bold">{{ esc['data_escala'] }} - {{ esc['tipo_culto'] }}</td>
                                    <td class="p-2.5 font-bold text-blue-900">{{ esc['pregador'] or '-' }}</td>
                                    <td class="p-2.5 text-center"><a href="/escalas/pdf/{{ esc['id'] }}" class="bg-blue-600 text-white px-3 py-1 rounded-lg font-bold">📄 PDF</a></td>
                                </tr>"""

linha_loop_nova = """                                {% set dt_parts = esc['data_escala'].split('-') if esc['data_escala'] else [] %}
                                <tr>
                                    <td class="p-2.5 font-bold">
                                        <div class="text-slate-900">{{ esc['data_escala'] }}</div>
                                        <span class="text-xs font-semibold text-indigo-600">{{ esc['tipo_culto'] }}</span>
                                    </td>
                                    <td class="p-2.5">
                                        <div class="font-bold text-slate-800">{{ esc['pregador'] or 'Não definido' }}</div>
                                        {% if esc['dirigente'] %}<div class="text-[11px] text-slate-500">Dirigente: {{ esc['dirigente'] }}</div>{% endif %}
                                    </td>
                                    <td class="p-2.5 text-center" id="status-escala-{{ esc['id'] }}">
                                        <!-- Calculado via JS -->
                                        <span class="badge-alerta text-[11px] font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600" data-data="{{ esc['data_escala'] }}">
                                            A verificar...
                                        </span>
                                    </td>
                                    <td class="p-2.5 text-center space-x-1.5 whitespace-nowrap">
                                        {% set texto_msg = "Paz do Senhor! Lembramos da escala na IEAD para o " ~ esc['tipo_culto'] ~ " no dia " ~ esc['data_escala'] ~ ". Pregador: " ~ (esc['pregador'] or 'A designar') ~ ". Dirigente: " ~ (esc['dirigente'] or 'A designar') ~ ". Deus abençoe!" %}
                                        <a href="https://wa.me/?text={{ texto_msg | urlencode }}" 
                                           target="_blank" 
                                           title="Enviar lembrete via WhatsApp"
                                           class="inline-flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1.5 rounded-lg text-xs font-black shadow transition">
                                            <span>💬 WhatsApp</span>
                                        </a>
                                        <a href="/escalas/pdf/{{ esc['id'] }}" class="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1.5 rounded-lg text-xs font-bold transition">
                                            📄 PDF
                                        </a>
                                    </td>
                                </tr>"""

if linha_loop_antiga in html:
    html = html.replace(linha_loop_antiga, linha_loop_nova)
    print("✓ Linhas de escalas atualizadas com WhatsApp e alerta!")
else:
    # Tentativa com correspondência normalizada de quebras de linha
    print("Aviso: Tentando correspondência alternativa para a linha da escala...")
    html = re.sub(
        r'<tr>\s*<td class="p-2\.5 font-bold">\{\{\s*esc\[\'data_escala\'\]\s*\}\} - \{\{\s*esc\[\'tipo_culto\'\]\s*\}\}</td>\s*<td class="p-2\.5 font-bold text-blue-900">\{\{\s*esc\[\'pregador\'\] or \'-\'\s*\}\}</td>\s*<td class="p-2\.5 text-center"><a href="/escalas/pdf/\{\{\s*esc\[\'id\'\]\s*\}\}".*?</td>\s*</tr>',
        linha_loop_nova,
        html,
        flags=re.DOTALL
    )

# 3. Adicionar o script que calcula se falta 1 ou 2 dias e colore o selo
script_alerta = """
    // Cálculo automático de dias para a escala
    document.addEventListener("DOMContentLoaded", function() {
        const badges = document.querySelectorAll(".badge-alerta");
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);

        badges.forEach(badge => {
            const dataStr = badge.getAttribute("data-data");
            if (!dataStr) return;
            
            const partes = dataStr.split("-");
            if (partes.length !== 3) return;
            
            const dataCulto = new Date(partes[0], partes[1] - 1, partes[2]);
            dataCulto.setHours(0, 0, 0, 0);
            
            const difDias = Math.round((dataCulto - hoje) / (1000 * 60 * 60 * 24));
            
            if (difDias === 0) {
                badge.className = "inline-block text-[11px] font-black px-2.5 py-1 rounded-full bg-rose-100 text-rose-700 border border-rose-300 animate-pulse";
                badge.innerHTML = "🔥 É Hoje!";
            } else if (difDias === 1) {
                badge.className = "inline-block text-[11px] font-black px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-300";
                badge.innerHTML = "⚡ É Amanhã!";
            } else if (difDias === 2) {
                badge.className = "inline-block text-[11px] font-black px-2.5 py-1 rounded-full bg-blue-100 text-blue-800 border border-blue-300";
                badge.innerHTML = "⏳ Faltam 2 dias";
            } else if (difDias > 2) {
                badge.className = "inline-block text-[11px] font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600";
                badge.innerHTML = "Em " + difDias + " dias";
            } else {
                badge.className = "inline-block text-[11px] font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-400";
                badge.innerHTML = "Realizado";
            }
        });
    });
"""

if "badge-alerta" not in html or "Cálculo automático de dias para a escala" not in html:
    # Insere antes de </body>
    if "</body>" in html:
        html = html.replace("</body>", f"<script>{script_alerta}</script>\n</body>")
        print("✓ Script de cálculo de antecedência injetado com sucesso!")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)