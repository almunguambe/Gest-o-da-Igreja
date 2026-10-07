with open('templates/superadmin_igrejas.html', 'r', encoding='utf-8') as f:
    html = f.read()

alvo = '<a href="/dashboard"'
novo_botao = '<a href="/superadmin/estatisticas" class="bg-indigo-600 hover:bg-indigo-500 text-white font-black text-xs px-3.5 py-2 rounded-xl shadow transition flex items-center gap-1.5">📊 Mapa Estatístico Geral</a>\n            <a href="/dashboard"'

if '/superadmin/estatisticas' not in html:
    if alvo in html:
        html = html.replace(alvo, novo_botao, 1)
        with open('templates/superadmin_igrejas.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✓ Botão do Mapa Estatístico adicionado ao cabeçalho do SuperAdmin!")
    else:
        print("! Ponto de ancoragem do link não encontrado no template.")
else:
    print("! Link já existia no template.")