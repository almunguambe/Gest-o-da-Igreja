with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Substituir o bloco de Naturalidade para comportar Estado Civil de forma elegante
bloco_antigo = """                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                            </div>

                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Filiação (Pai & Mãe)</label>"""

bloco_novo = """                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
                                </div>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">💍 Estado Civil</label>
                                    <select name="estado_civil" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-semibold focus:border-indigo-600">
                                        <option value="Solteiro(a)">Solteiro(a)</option>
                                        <option value="Casado(a) no Religioso">Casado(a) no Religioso</option>
                                        <option value="Casado(a) no Civil">Casado(a) no Civil</option>
                                        <option value="Casado(a) Religioso & Civil">Casado(a) Religioso & Civil</option>
                                        <option value="Viúvo(a)">Viúvo(a)</option>
                                        <option value="Divorciado(a)">Divorciado(a)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-slate-700 mb-1">Filiação (Pai & Mãe)</label>
                                    <input type="text" name="filiacao" placeholder="Nome dos pais..." class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                                </div>
                            </div>"""

if bloco_antigo in conteudo:
    conteudo = conteudo.replace(bloco_antigo, bloco_novo)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Campo Estado Civil adicionado com sucesso ao formulário de membros!")
else:
    print("! Bloco padrão não encontrado de forma idêntica. Verificando...")