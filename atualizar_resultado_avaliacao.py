with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

trecho_antigo = """    if status == "Aprovado":
        proxima = classe.get('proxima')
        if proxima:
            return redirect(f"/discipulado/classe/{proxima}")
        else:
            return redirect(f"/discipulado/classe/{cid}")
    else:
        return redirect(f"/discipulado/classe/{cid}")"""

trecho_novo = """    proxima = classe.get('proxima')
    proxima_url = f"/discipulado/classe/{proxima}" if proxima else f"/discipulado/classe/{cid}"
    repetir_url = f"/discipulado/classe/{cid}/avaliacao"
    
    html_resultado = f\"\"\"
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultado da Avaliação - IEAD Chicuque</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-900/80 min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-md w-full p-6 sm:p-8 text-center space-y-6">
            <div class="w-20 h-20 mx-auto rounded-3xl {'bg-emerald-100 text-emerald-600' if status == 'Aprovado' else 'bg-amber-100 text-amber-600'} flex items-center justify-center text-4xl shadow-inner">
                {'🏆' if status == 'Aprovado' else '📖'}
            </div>

            <div class="space-y-2">
                <span class="text-[11px] font-black uppercase tracking-widest px-3 py-1 rounded-full {'bg-emerald-50 text-emerald-700 border border-emerald-200' if status == 'Aprovado' else 'bg-amber-50 text-amber-700 border border-amber-200'}">
                    {'Aprovado na Classe' if status == 'Aprovado' else 'Necessário Reforço'}
                </span>
                <h2 class="text-2xl font-black text-slate-900">
                    {'Parabéns!' if status == 'Aprovado' else 'Quase lá!'}
                </h2>
                <p class="text-slate-600 text-sm font-medium">
                    Alcançou <b>{acertos} de {total_questoes}</b> acertos com aproveitamento de <span class="font-extrabold text-slate-900">{nota_final:.0f}%</span>.
                </p>
                {'<p class="text-[12px] text-slate-500">O aproveitamento mínimo para avançar é de 70%.</p>' if status != 'Aprovado' else ''}
            </div>

            <div class="pt-2 flex flex-col gap-2.5">
                {'<a href=\"' + proxima_url + '\" class=\"w-full py-3.5 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm shadow-lg shadow-emerald-600/30 transition\">Avançar para a Próxima Classe ➔</a>' if status == 'Aprovado' else '<a href=\"' + repetir_url + '\" class=\"w-full py-3.5 px-6 rounded-2xl bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-sm shadow-lg shadow-amber-600/30 transition\">Rever Lições e Tentar Novamente ↺</a>'}
                <a href="/discipulado/classe/{cid}" class="w-full py-2.5 px-6 rounded-2xl text-slate-500 hover:text-slate-800 text-xs font-bold transition">
                    Voltar ao Índice da Classe
                </a>
            </div>
        </div>
    </body>
    </html>
    \"\"\"
    return render_template_string(html_resultado)"""

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Tela/Modal de resultado de avaliação atualizada com sucesso no app.py!")
else:
    print("! Trecho antigo não localizado diretamente. Verifique se já foi modificado.")