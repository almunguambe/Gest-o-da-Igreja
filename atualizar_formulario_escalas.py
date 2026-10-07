with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Substituir os campos do formulário para incluir contactos
campos_form_antigos = """                            <input type="text" name="dirigente" placeholder="Dirigente" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            <input type="text" name="pregador" placeholder="Pregador" class="w-full h-11 px-3 text-sm border-2 rounded-xl">"""

campos_form_novos = """                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-[11px] font-bold text-slate-700 mb-1">Dirigente</label>
                                    <input type="text" name="dirigente" placeholder="Nome do Dirigente" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                                <div>
                                    <label class="block text-[11px] font-bold text-slate-700 mb-1">Contacto Dirigente</label>
                                    <input type="text" name="telefone_dirigente" placeholder="Ex: 841234567" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600 font-mono">
                                </div>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-[11px] font-bold text-slate-700 mb-1">Pregador</label>
                                    <input type="text" name="pregador" placeholder="Nome do Pregador" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                                <div>
                                    <label class="block text-[11px] font-bold text-slate-700 mb-1">Contacto Pregador</label>
                                    <input type="text" name="telefone_pregador" placeholder="Ex: 841234567" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600 font-mono">
                                </div>
                            </div>"""

if campos_form_antigos in html:
    html = html.replace(campos_form_antigos, campos_form_novos)
    print("✓ Campos de contacto do Pregador e Dirigente inseridos no formulário!")
else:
    print("- Aviso: trecho antigo do formulário não encontrado exato.")

# 2. Atualizar as ações na tabela para gerar links de WhatsApp e SMS direto com o número
trecho_acoes_antigo = """                                    <td class="p-2.5 text-center space-x-1.5 whitespace-nowrap">
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
                                    </td>"""

trecho_acoes_novo = """                                    <td class="p-2.5 text-center whitespace-nowrap">
                                        {% set tel_dest = (esc['telefone_pregador'] or esc['telefone_dirigente'] or '') | replace(' ', '') | replace('+', '') %}
                                        {% if tel_dest and not tel_dest.startswith('258') and tel_dest|length == 9 %}
                                            {% set tel_dest = '258' ~ tel_dest %}
                                        {% endif %}
                                        {% set texto_msg = "Paz do Senhor! Lembramos a sua escala na IEAD para o culto de " ~ esc['data_escala'] ~ " (" ~ esc['tipo_culto'] ~ "). Pregador: " ~ (esc['pregador'] or 'A designar') ~ " | Dirigente: " ~ (esc['dirigente'] or 'A designar') ~ ". Deus abençoe!" %}
                                        
                                        <div class="inline-flex items-center gap-1">
                                            {% if tel_dest %}
                                                <a href="https://wa.me/{{ tel_dest }}?text={{ texto_msg | urlencode }}" 
                                                   target="_blank" 
                                                   title="Enviar WhatsApp direto para {{ tel_dest }}"
                                                   class="inline-flex items-center bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded-lg text-[11px] font-black shadow transition">
                                                    💬 Whats
                                                </a>
                                                <a href="sms:+{{ tel_dest }}?body={{ texto_msg | urlencode }}" 
                                                   title="Enviar SMS direto para {{ tel_dest }}"
                                                   class="inline-flex items-center bg-amber-600 hover:bg-amber-700 text-white px-2 py-1 rounded-lg text-[11px] font-black shadow transition">
                                                    📩 SMS
                                                </a>
                                            {% else %}
                                                <a href="https://wa.me/?text={{ texto_msg | urlencode }}" 
                                                   target="_blank" 
                                                   title="Enviar WhatsApp (selecionar contacto)"
                                                   class="inline-flex items-center bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded-lg text-[11px] font-black shadow transition">
                                                    💬 Whats
                                                </a>
                                            {% endif %}
                                            <a href="/escalas/pdf/{{ esc['id'] }}" class="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded-lg text-[11px] font-bold transition">
                                                📄 PDF
                                            </a>
                                        </div>
                                    </td>"""

if trecho_acoes_antigo in html:
    html = html.replace(trecho_acoes_antigo, trecho_acoes_novo)
    print("✓ Botões de WhatsApp e SMS com número direto aplicados!")
else:
    print("- Aviso: trecho de ações antigo não coincidiu exato.")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)