with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Bloco estruturado com os 4 campos de localização
bloco_campos_localizacao = '''
                    <!-- Localização Eclesiástica e Residencial -->
                    <div class="col-span-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <div>
                            <label class="block text-xs font-black text-slate-700 uppercase tracking-wide mb-1">
                                Zona <span class="text-rose-500">* (Obrigatório)</span>
                            </label>
                            <input type="text" name="zona" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900 font-semibold" placeholder="Ex: Zona Central / Zona 3" required>
                        </div>
                        <div>
                            <label class="block text-xs font-black text-slate-700 uppercase tracking-wide mb-1">
                                Célula
                            </label>
                            <input type="text" name="celula" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900" placeholder="Ex: Célula Betel">
                        </div>
                        <div>
                            <label class="block text-xs font-black text-slate-700 uppercase tracking-wide mb-1">
                                Bairro
                            </label>
                            <input type="text" name="bairro" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900" placeholder="Ex: Chicuque">
                        </div>
                        <div>
                            <label class="block text-xs font-black text-slate-700 uppercase tracking-wide mb-1">
                                Distrito
                            </label>
                            <input type="text" name="distrito" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:border-blue-900" placeholder="Ex: Maxixe">
                        </div>
                    </div>
'''

# Se houver campo de bairro isolado, substitui pelo bloco completo dos 4 campos
if 'name="bairro"' in html:
    partes = html.split('name="bairro"')
    inicio = partes[0].rsplit('<div', 1)[0]
    resto = partes[1].split('</div>', 1)[1]
    html = inicio + bloco_campos_localizacao + resto

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Formulário atualizado com Zona (obrigatória), Célula, Bairro e Distrito!")