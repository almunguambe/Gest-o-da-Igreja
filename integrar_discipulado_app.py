with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Injetar o import do novo módulo
import_modulo = "from modulo_escola_biblica import CURRICULO_CLASSES, gerar_pdf_conclusao_discipulado\n"
if "from modulo_escola_biblica import" not in conteudo:
    conteudo = import_modulo + conteudo

# Rotas de avaliação, progresso e emissão do certificado
bloco_rotas = '''
# ==============================================================================
# DISCIPULADO BÍBLICO PROGRESSIVO & CERTIFICADO DE CONCLUSÃO
# ==============================================================================
@app.route('/discipulado/classe/<cid>')
def ver_classe_discipulado(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe não encontrada", 404

    classe = CURRICULO_CLASSES[cid]
    # Recupera o primeiro membro cadastrado para vincular a sessão de teste
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, nome FROM membros ORDER BY id ASC LIMIT 1")
    membro = c.fetchone()
    
    # Obter histórico de aprovações
    m_id = membro['id'] if hasattr(membro, 'keys') else (membro[0] if membro else 1)
    c.execute("SELECT classe_id, nota, status FROM progresso_discipulado WHERE membro_id = %s" if DATABASE_URL and psycopg2 else "SELECT classe_id, nota, status FROM progresso_discipulado WHERE membro_id = ?", (m_id,))
    registos = c.fetchall()
    conn.close()

    aprovadas = set()
    for r in registos:
        c_id = r['classe_id'] if hasattr(r, 'keys') else r[0]
        st = r['status'] if hasattr(r, 'keys') else r[2]
        if st == 'Aprovado':
            aprovadas.add(c_id)

    # Verificar bloqueio progressivo
    bloqueada = False
    if cid == 'c2' and 'c1' not in aprovadas:
        bloqueada = True
    elif cid == 'c3' and ('c1' not in aprovadas or 'c2' not in aprovadas):
        bloqueada = True
    elif cid == 'c4' and ('c1' not in aprovadas or 'c2' not in aprovadas or 'c3' not in aprovadas):
        bloqueada = True

    concluiu_todas = ('c1' in aprovadas and 'c2' in aprovadas and 'c3' in aprovadas and 'c4' in aprovadas)

    from flask import render_template_string
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{{ classe.nome }} - IEAD Chicuque</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8fafc; font-family: 'Segoe UI', sans-serif; }
            .card-aula { border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
            .card-header-aula { background: #0d3b66; color: white; border-radius: 12px 12px 0 0; padding: 12px 20px; font-weight: bold; }
            .badge-ouro { background: #d4af37; color: #111; font-weight: bold; }
        </style>
    </head>
    <body class="p-3 p-md-5">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <div>
                    <h2 class="text-primary fw-bold mb-0">{{ classe.nome }}</h2>
                    <span class="text-muted">{{ classe.duracao }} • 6 Lições Exclusivas</span>
                </div>
                <div>
                    <a href="/estudos" class="btn btn-outline-secondary">← Voltar às Classes</a>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-success fw-bold">🎓 Emitir Certificado de Conclusão</a>
                    {% endif %}
                </div>
            </div>

            <!-- Navegador de Classes -->
            <div class="d-flex gap-2 mb-4 overflow-auto pb-2">
                <a href="/discipulado/classe/c1" class="btn btn-sm {% if cid == 'c1' %}btn-primary{% else %}btn-light border{% endif %}">Classe I {% if 'c1' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c2" class="btn btn-sm {% if cid == 'c2' %}btn-primary{% else %}btn-light border{% endif %}">Classe II {% if 'c2' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c3" class="btn btn-sm {% if cid == 'c3' %}btn-primary{% else %}btn-light border{% endif %}">Classe III {% if 'c3' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c4" class="btn btn-sm {% if cid == 'c4' %}btn-primary{% else %}btn-light border{% endif %}">Classe IV {% if 'c4' in aprovadas %}✓{% endif %}</a>
            </div>

            {% if bloqueada %}
            <div class="alert alert-warning p-4 rounded-3 text-center">
                <h4 class="fw-bold">Classe Bloqueada 🔒</h4>
                <p class="mb-0">Para estudar esta classe, é necessário primeiro responder ao questionário da classe anterior e obter aprovação com nota mínima de 70%.</p>
            </div>
            {% else %}
                <h4 class="fw-bold mb-3 text-dark">Matéria Completa das 6 Lições</h4>
                {% for lic in classe.licoes %}
                <div class="card card-aula">
                    <div class="card-header card-header-aula d-flex justify-content-between">
                        <span>Lição {{ lic.numero }}: {{ lic.titulo }}</span>
                        <span class="badge badge-ouro">{{ lic.versiculo }}</span>
                    </div>
                    <div class="card-body p-4">
                        <p class="mb-0 text-secondary" style="font-size: 1.05rem; line-height: 1.7;">{{ lic.conteudo }}</p>
                    </div>
                </div>
                {% endfor %}

                <!-- Questionário da Classe -->
                <div class="card border-0 shadow-sm rounded-4 mt-5">
                    <div class="card-header bg-dark text-white p-3 rounded-top-4">
                        <h5 class="mb-0 fw-bold">📝 Prova de Avaliação da {{ classe.nome }}</h5>
                        <small class="text-light">Responda a todas as questões para desbloquear a classe seguinte.</small>
                    </div>
                    <div class="card-body p-4">
                        <form action="/discipulado/avaliar/{{ cid }}" method="POST">
                            <input type="hidden" name="membro_id" value="{{ m_id }}">
                            {% for q in classe.questionario %}
                            <div class="mb-4">
                                <p class="fw-bold text-dark mb-2">{{ loop.index }}. {{ q.pergunta }}</p>
                                {% for op in q.opcoes %}
                                <div class="form-check mb-1">
                                    <input class="form-check-input" type="radio" name="resp_{{ q.id }}" value="{{ loop.index0 }}" id="q_{{ q.id }}_{{ loop.index0 }}" required>
                                    <label class="form-check-label text-secondary" for="q_{{ q.id }}_{{ loop.index0 }}">{{ op }}</label>
                                </div>
                                {% endfor %}
                            </div>
                            {% endfor %}
                            <button type="submit" class="btn btn-primary px-4 py-2 fw-bold">Submeter Avaliação e Desbloquear Próxima Classe</button>
                        </form>
                    </div>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, classe=classe, cid=cid, bloqueada=bloqueada, aprovadas=aprovadas, concluiu_todas=concluiu_todas, m_id=m_id)

@app.route('/discipulado/avaliar/<cid>', methods=['POST'])
def processar_avaliacao_discipulado(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe inválida", 400

    classe = CURRICULO_CLASSES[cid]
    from flask import request, redirect, flash
    m_id = request.form.get('membro_id', 1)

    total_questoes = len(classe['questionario'])
    acertos = 0
    for q in classe['questionario']:
        resp_escolhida = request.form.get(f"resp_{q['id']}")
        if resp_escolhida is not None and int(resp_escolhida) == q['correta']:
            acertos += 1

    nota_final = (acertos / total_questoes) * 100
    status = "Aprovado" if nota_final >= 70 else "Reprovado"

    # Gravar na base de dados
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
        VALUES (%s, %s, %s, %s)
    """ if DATABASE_URL and psycopg2 else """
        INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
        VALUES (?, ?, ?, ?)
    """, (m_id, cid, nota_final, status))
    conn.commit()
    conn.close()

    if status == "Aprovado":
        proxima = classe.get('proxima')
        if proxima:
            return redirect(f"/discipulado/classe/{proxima}")
        else:
            return redirect(f"/discipulado/classe/{cid}")
    else:
        return redirect(f"/discipulado/classe/{cid}")

@app.route('/membro/<int:id>/certificado_conclusao_discipulado')
def emitir_certificado_conclusao(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado", 404

        dados = extrair_dados_membro(membro)
        buffer = gerar_pdf_conclusao_discipulado(dados, obter_caminho_logo)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Certificado_Conclusao_Discipulado_{id}.pdf")
    except Exception as e:
        return f"Erro ao gerar certificado de conclusão: {e}", 500
'''

if "def ver_classe_discipulado(" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", bloco_rotas + "\nif __name__ ==")
    else:
        conteudo += "\n" + bloco_rotas

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Discipulado progressivo de 24 lições e Certificado de Conclusão integrados!")