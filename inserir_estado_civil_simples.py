with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Campo Estado Civil completo, limpo e sem JS dinâmico
campo_estado_civil = '''
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">💍 Estado Civil</label>
                                <select name="estado_civil" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-semibold focus:border-indigo-600">
                                    <option value="Solteiro(a)">Solteiro(a)</option>
                                    <option value="Casado(a) no Religioso">Casado(a) no Religioso</option>
                                    <option value="Casado(a) no Civil">Casado(a) no Civil</option>
                                    <option value="Casado(a) Religioso & Civil">Casado(a) Religioso & Civil</option>
                                    <option value="Viúvo(a)">Viúvo(a)</option>
                                    <option value="Divorciado(a)">Divorciado(a)</option>
                                    <option value="Criança / Menor">Criança / Menor</option>
                                </select>
                            </div>
'''

# Inserir imediatamente antes do campo de Filiação, mantendo todo o resto intocado
alvo = '<div>\n                                <label class="block text-xs font-bold text-slate-700 mb-1">Filiação (Pai & Mãe)</label>'

if "name=\"estado_civil\"" not in conteudo:
    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, campo_estado_civil + alvo)
        print("✓ Campo Estado Civil inserido antes de Filiação com total segurança!")
    else:
        # Fallback caso haja diferença mínima de indentação
        import re
        conteudo = re.sub(r'(<div>\s*<label[^>]*>Filiação.*?</label>)', campo_estado_civil + r'\1', conteudo, count=1)
        print("✓ Campo Estado Civil inserido via regex!")
else:
    print("O campo estado_civil já está presente.")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)