with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Cortar qualquer resíduo após </html>
pos_html = conteudo.find('</html>')
if pos_html != -1:
    conteudo = conteudo[:pos_html + 7] + "\n"
    print("✓ Resíduo após </html> removido com sucesso!")

# 2. Localizar o bloco antigo de botões dentro da tabela de escalas legítima (por volta da linha 585)
trecho_antigo = """                                        <div class="inline-flex items-center gap-1">
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
                                                    ✉️ SMS
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
                                        </div>"""

trecho_novo = """                                        <div class="flex flex-col sm:flex-row items-center justify-center gap-1.5">
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
                                            {% endif %}

                                            <a href="/escalas/pdf/{{ esc['id'] }}" class="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded-lg text-[11px] font-bold transition">
                                                📄 PDF
                                            </a>
                                        </div>"""

if "Criar Escala de Culto" in conteudo:
    # Substituir de forma resiliente
    import re
    padrao = r'<div class="inline-flex items-center gap-1">.*?<a href="/escalas/pdf/\{\{ esc\[\'id\'\] \}\}".*?<\/div>'
    if re.search(padrao, conteudo, flags=re.DOTALL):
        conteudo = re.sub(padrao, trecho_novo.strip(), conteudo, flags=re.DOTALL)
        print("✓ Botões inteligentes aplicados no local correto via regex!")
    else:
        print("! Padrão antigo não encontrado diretamente; verificando se já possui os novos botões.")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)