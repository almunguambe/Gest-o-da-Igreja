with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Bloco antigo da coluna de Ações
antigo = """                                         <div class="inline-flex items-center gap-1">
                                             {% if tel_dest %}
                                                 <a href="https://wa.me/{{ tel_dest }}?text={{ texto_msg | urlencode }}"
                                                    target="_blank"
                                                    title="Enviar WhatsApp direto para {{ tel_dest }}"
                                                    class="inline-flex items-center bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded-lg text-[11px] font-black shadow transition">
                                                     💬 Whats
                                                 </a>
                                                 <a href="sms:+{{ tel_dest }}?body={{ texto_msg | urlencode }}"
                                                    title="Enviar SMS direto para {{ tel_dest }}"
                                                    class="inline-flex items-center bg-amber-600 hover:bg-amber-700 text-white px-2 py-1 rounded-lg text-[11px] font-black shadow transition">"""

novo = """                                         <div class="flex flex-col sm:flex-row items-center justify-center gap-1.5">
                                             {% set tel_dir = (esc['telefone_dirigente'] or '') | replace(' ', '') | replace('+', '') %}
                                             {% if tel_dir and not tel_dir.startswith('258') and tel_dir|length == 9 %}{% set tel_dir = '258' ~ tel_dir %}{% endif %}
                                             
                                             {% set tel_preg = (esc['telefone_pregador'] or '') | replace(' ', '') | replace('+', '') %}
                                             {% if tel_preg and not tel_preg.startswith('258') and tel_preg|length == 9 %}{% set tel_preg = '258' ~ tel_preg %}{% endif %}

                                             {% set msg_dir = "Graça e Paz, amado(a) " ~ (esc['dirigente'] or 'Obreiro') ~ "!\\n\\nConfirmamos a sua escala como *DIRIGENTE* na IEAD Chicuque:\\n📅 *Data:* " ~ esc['data_escala'] ~ "\\n⛪ *Culto:* " ~ esc['tipo_culto'] ~ "\\n📖 *Leitura Inicial:* " ~ (esc['leitura_palavra'] or 'A definir') ~ "\\n🎙️ *Pregador:* " ~ (esc['pregador'] or 'A definir') ~ "\\n\\nPedimos a comparência com 30 minutos de antecedência. Confirme o recebimento desta mensagem. Deus abençoe!" %}
                                             
                                             {% set msg_preg = "Graça e Paz, amado(a) " ~ (esc['pregador'] or 'Obreiro') ~ "!\\n\\nConfirmamos a sua escala para a *MINISTRAÇÃO DA PALAVRA (Pregador)* na IEAD Chicuque:\\n📅 *Data:* " ~ esc['data_escala'] ~ "\\n⛪ *Culto:* " ~ esc['tipo_culto'] ~ "\\n👤 *Dirigente:* " ~ (esc['dirigente'] or 'A definir') ~ "\\n\\nContamos com a sua oração e preparação. Confirme a recepção. Deus abençoe o ministério!" %}

                                             {% if tel_dir %}
                                                 <a href="https://wa.me/{{ tel_dir }}?text={{ msg_dir | urlencode }}" target="_blank"
                                                    title="Notificar Dirigente ({{ esc['dirigente'] }})"
                                                    class="inline-flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded-lg text-[10px] font-bold shadow transition">
                                                     <span>📲</span> Dirigente
                                                 </a>
                                             {% endif %}

                                             {% if tel_preg %}
                                                 <a href="https://wa.me/{{ tel_preg }}?text={{ msg_preg | urlencode }}" target="_blank"
                                                    title="Notificar Pregador ({{ esc['pregador'] }})"
                                                    class="inline-flex items-center gap-1 bg-indigo-600 hover:bg-indigo-700 text-white px-2.5 py-1 rounded-lg text-[10px] font-bold shadow transition">
                                                     <span>🎙️</span> Pregador
                                                 </a>
                                             {% endif %}

                                             {% if not tel_dir and not tel_preg %}
                                                 <span class="text-[10px] text-slate-400 italic">Sem contacto</span>
                                             {% endif %}"""

if antigo in html:
    html = html.replace(antigo, novo)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Botões inteligentes de notificação aplicados com sucesso!")
else:
    # Busca alternativa se houver variação de indentação
    idx_start = html.find('{% set tel_dest = (esc[\'telefone_pregador\']')
    idx_end = html.find('<a href="sms:+{{ tel_dest }}', idx_start)
    if idx_start != -1 and idx_end != -1:
        # Pega a linha do div container
        div_start = html.rfind('<div class="inline-flex items-center gap-1">', 0, idx_start)
        div_end = html.find('</a>', idx_end) + 4
        html = html[:div_start] + novo + html[div_end:]
        with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ Botões inteligentes aplicados via substituição de bloco!")
    else:
        print("! Bloco não encontrado automaticamente. Vamos verificar o trecho exato.")