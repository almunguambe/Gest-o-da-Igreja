with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Corrigir o caminho do logótipo para o ficheiro real logo.png
html = html.replace('/static/logo.svg?v=2026', "{{ url_for('static', filename='logo.png') }}")
html = html.replace('/static/logo.jpg', "{{ url_for('static', filename='logo.png') }}")

# 2. Separar Bairro e Zona na Ficha de Membro
trecho_bairro_antigo = """                            <div class="grid grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Bairro / Zona</label>
                                    <select name="bairro" class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white">
                                        <option value="">-- Selecione --</option>
                                        {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                                </div>
                            </div>"""

trecho_bairro_novo = """                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Zona Eclesiástica</label>
                                    <select name="zona" class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white focus:border-indigo-600">
                                        <option value="">-- Selecione a Zona --</option>
                                        {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Bairro / Residência</label>
                                    <input type="text" name="bairro" placeholder="Ex: Chicuque Sede, Maxixe..." class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                            </div>"""

if trecho_bairro_antigo in html:
    html = html.replace(trecho_bairro_antigo, trecho_bairro_novo, 1)
    print("✓ Bairro e Zona separados com sucesso!")
else:
    print("- Trecho de Bairro/Zona já modificado ou com espaçamento diferente.")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Logótipo atualizado para logo.png!")