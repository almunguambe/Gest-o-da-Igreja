import re

with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Substituir a função processar_avaliacao_discipulado inteira por uma versão blindada
padrao = r'def processar_avaliacao_discipulado\(cid\):.*?(?=@app\.route|\Z)'

nova_funcao = '''def processar_avaliacao_discipulado(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe inválida", 400

    from flask import request, render_template_string, session

    classe = CURRICULO_CLASSES[cid]
    m_id = request.form.get('membro_id', 1)
    try:
        m_id = int(m_id)
    except:
        m_id = 1

    total_questoes = len(classe['questionario'])
    acertos = 0
    for q in classe['questionario']:
        resp_escolhida = request.form.get(f"resp_{q['id']}")
        if resp_escolhida is not None:
            try:
                if int(resp_escolhida) == int(q['correta']):
                    acertos += 1
            except:
                pass

    nota_final = int((acertos / total_questoes) * 100) if total_questoes > 0 else 0
    status = "Aprovado" if nota_final >= 70 else "Reprovado"

    # Gravar progresso de forma segura
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS progresso_discipulado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER,
                classe_id TEXT,
                nota REAL,
                status TEXT,
                data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
            VALUES (?, ?, ?, ?)
        """, (m_id, cid, nota_final, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso ao salvar progresso: {e}")

    proxima = classe.get('proxima')
    proxima_url = f"/discipulado/classe/{proxima}" if proxima else f"/discipulado/classe/{cid}"
    repetir_url = f"/discipulado/classe/{cid}/avaliacao"

    cor_bg = "bg-emerald-100 text-emerald-600" if status == "Aprovado" else "bg-amber-100 text-amber-600"
    icone = "🏆" if status == "Aprovado" else "📖"
    tag_classe = "bg-emerald-50 text-emerald-700 border-emerald-200" if status == "Aprovado" else "bg-amber-50 text-amber-700 border-amber-200"
    rotulo = "Aprovado na Classe" if status == "Aprovado" else "Necessário Reforço"
    titulo = "Parabéns!" if status == "Aprovado" else "Quase lá!"

    if status == "Aprovado":
        botao_acao = f'<a href="{proxima_url}" class="w-full py-3.5 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm shadow-lg shadow-emerald-600/30 transition block">Avançar para a Próxima Classe ➔</a>'
    else:
        botao_acao = f'<a href="{repetir_url}" class="w-full py-3.5 px-6 rounded-2xl bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-sm shadow-lg shadow-amber-600/30 transition block">Rever Lições e Tentar Novamente ↺</a>'

    html_resultado = f"""<!DOCTYPE html>
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
        <div class="w-20 h-20 mx-auto rounded-3xl {cor_bg} flex items-center justify-center text-4xl shadow-inner">
            {icone}
        </div>

        <div class="space-y-2">
            <span class="text-[11px] font-black uppercase tracking-widest px-3 py-1 rounded-full border {tag_classe}">
                {rotulo}
            </span>
            <h2 class="text-2xl font-black text-slate-900">
                {titulo}
            </h2>
            <p class="text-slate-600 text-sm font-medium">
                Alcançou <b>{acertos} de {total_questoes}</b> acertos com aproveitamento de <span class="font-extrabold text-slate-900">{nota_final}%</span>.
            </p>
        </div>

        <div class="pt-2 flex flex-col gap-2.5">
            {botao_acao}
            <a href="/discipulado/classe/{cid}" class="w-full py-2.5 px-6 rounded-2xl text-slate-500 hover:text-slate-800 text-xs font-bold transition block">
                Voltar ao Índice da Classe
            </a>
        </div>
    </div>
</body>
</html>"""

    return render_template_string(html_resultado)

'''

conteudo_novo = re.sub(padrao, nova_funcao, conteudo, count=1, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo_novo)

print("✓ Função processar_avaliacao_discipulado corrigida com sucesso!")