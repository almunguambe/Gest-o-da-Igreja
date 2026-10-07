with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

antigo_campo = '<input type="text" name="descricao" required placeholder="Descrição / Detalhes *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">'

novos_campos = """<input type="text" name="descricao" required placeholder="Descrição / Detalhes *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            <div class="grid grid-cols-2 gap-2">
                                <select name="metodo_pagamento" class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white font-bold">
                                    <option value="Dinheiro">💵 Dinheiro / Espécie</option>
                                    <option value="M-Pesa">📱 M-Pesa</option>
                                    <option value="e-Mola">📱 e-Mola</option>
                                    <option value="Banco">🏦 Depósito / Transferência</option>
                                </select>
                                <input type="text" name="referencia_transacao" placeholder="Cód. Transação / Ref. (opcional)" class="w-full h-11 px-3 text-xs border-2 rounded-xl font-mono">
                            </div>"""

if antigo_campo in conteudo:
    conteudo = conteudo.replace(antigo_campo, novos_campos, 1)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Campos de M-Pesa, e-Mola e Referência adicionados com sucesso ao Dashboard!")
else:
    print("! Campo antigo não localizado no template.")