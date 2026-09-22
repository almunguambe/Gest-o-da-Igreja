with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

novo_bloco_licao_por_licao = '''
# ==============================================================================
# DISCIPULADO: LIÇÃO A LIÇÃO COM PROGRESSÃO E DÚVIDAS ESPECÍFICAS
# ==============================================================================
@app.route('/discipulado/classe/<cid>')
def redirecionar_primeira_licao(cid):
    return redirect(f"/discipulado/classe/{cid}/licao/0")

@app.route('/discipulado/classe/<cid>/licao/<int:lid>')
def ver_licao_individual(cid, lid):
    if cid not in CURRICULO_CLASSES:
        return "Classe não encontrada", 404

    classe = CURRICULO_CLASSES[cid]
    total_licoes = len(classe['licoes'])
    if lid < 0 or lid >= total_licoes:
        return redirect(f"/discipulado/classe/{cid}/licao/0")

    licao_atual = classe['licoes'][lid]
    tem_anterior = (lid > 0)
    tem_proxima = (lid < total_licoes - 1)
    url_anterior = f"/discipulado/classe/{cid}/licao/{lid - 1}" if tem_anterior else "#"
    url_proxima = f"/discipulado/classe/{cid}/licao/{lid + 1}" if tem_proxima else f"/discipulado/classe/{cid}/avaliacao"

    # Verificar progresso de classes
    aprovadas = set()
    m_id = 1
    nome_membro = "Aluno"

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS duvidas_discipulado (
                id SERIAL PRIMARY KEY,
                membro_id INTEGER,
                membro_nome VARCHAR(150),
                classe_nome VARCHAR(100),
                licao_titulo VARCHAR(150),
                duvida TEXT,
                resposta TEXT,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """ if DATABASE_URL and psycopg2 else """
            CREATE TABLE IF NOT EXISTS duvidas_discipulado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER,
                membro_nome TEXT,
                classe_nome TEXT,
                licao_titulo TEXT,
                duvida TEXT,
                resposta TEXT,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        c.execute("SELECT id, nome FROM membros ORDER BY id ASC LIMIT 1")
        m = c.fetchone()
        if m:
            if hasattr(m, 'keys') and 'id' in m.keys():
                m_id = m['id']
                nome_membro = m['nome']
            elif isinstance(m, dict) and 'id' in m:
                m_id = m['id']
                nome_membro = m['nome']
            else:
                m_id = m[0]
                nome_membro = m[1] if len(m) > 1 else "Aluno"

        c.execute("SELECT classe_id, status FROM progresso_discipulado WHERE membro_id = %s" if DATABASE_URL and psycopg2 else "SELECT classe_id, status FROM progresso_discipulado WHERE membro_id = ?", (m_id,))
        for r in c.fetchall():
            c_id = r['classe_id'] if hasattr(r, 'keys') else r[0]
            st = r['status'] if hasattr(r, 'keys') else r[1]
            if st == 'Aprovado':
                aprovadas.add(str(c_id).strip())
        conn.close()
    except Exception as e:
        print(f"Erro ao verificar sessao da licao: {e}")

    # Checagem de bloqueio progressivo
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
    <html lang="pt">
    <head>
        <meta charset="utf-8">
        <title>Lição {{ licao_atual.numero }} - {{ classe.nome }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f1f5f9; font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; }
            .card-estudo { border: none; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.05); background: #ffffff; overflow: hidden; }
            .header-top { background: #0d3b66; color: white; padding: 20px 24px; border-bottom: 4px solid #d4af37; }
            .conteudo-texto { font-size: 1.1rem; line-height: 1.85; color: #334155; }
            .badge-ref { background: #d4af37; color: #0d3b66; font-weight: 700; padding: 6px 14px; border-radius: 20px; font-size: 0.9rem; }
            .btn-next { background: #0d3b66; color: white; font-weight: 700; padding: 12px 28px; border-radius: 10px; transition: all 0.2s ease; border: none; text-decoration: none; }
            .btn-next:hover { background: #082642; color: #fff; transform: translateY(-1px); }
            .btn-prev { background: #e2e8f0; color: #475569; font-weight: 600; padding: 12px 24px; border-radius: 10px; text-decoration: none; }
            .btn-prev:hover { background: #cbd5e1; color: #1e293b; }
            .card-duvida { background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 14px; padding: 24px; margin-top: 35px; }
        </style>
    </head>
    <body class="py-4">
        <div class="container" style="max-width: 860px;">
            <!-- Barra Superior -->
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                <div>
                    <a href="/" class="text-decoration-none text-muted fw-bold">← Início</a>
                    <span class="text-muted mx-2">/</span>
                    <span class="text-primary fw-semibold">{{ classe.nome }}</span>
                </div>
                <div class="d-flex gap-2">
                    <span class="badge bg-white text-dark border px-3 py-2 fw-semibold">Lição {{ lid + 1 }} de {{ total_licoes }}</span>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-sm btn-success fw-bold">🎓 Certificado</a>
                    {% endif %}
                </div>
            </div>

            {% if bloqueada %}
            <div class="card-estudo p-5 text-center my-4">
                <div style="font-size: 3rem;">🔒</div>
                <h3 class="fw-bold mt-3 mb-2" style="color: #0d3b66;">Classe Bloqueada</h3>
                <p class="text-secondary mx-auto" style="max-width: 500px;">Para estudar esta lição, conclua primeiro o questionário da classe anterior com aproveitamento mínimo de 70%.</p>
                <a href="/discipulado/classe/c1" class="btn btn-primary px-4 py-2 mt-2 fw-bold">Ir para a Classe I</a>
            </div>
            {% else %}
            <!-- Card Principal da Lição Atual -->
            <div class="card-estudo">
                <div class="header-top d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <div>
                        <small class="text-warning text-uppercase fw-bold tracking-wide">Lição {{ licao_atual.numero }}</small>
                        <h3 class="fw-bold mb-0 text-white mt-1">{{ licao_atual.titulo }}</h3>
                    </div>
                    {% if licao_atual.versiculo %}
                    <span class="badge-ref">{{ licao_atual.versiculo }}</span>
                    {% endif %}
                </div>
                <div class="card-body p-4 p-md-5">
                    <div class="conteudo-texto">
                        {{ licao_atual.conteudo | safe }}
                    </div>

                    <!-- Navegação Próxima / Anterior -->
                    <div class="d-flex justify-content-between align-items-center mt-5 pt-4 border-top flex-wrap gap-2">
                        {% if tem_anterior %}
                        <a href="{{ url_anterior }}" class="btn-prev">« Lição Anterior</a>
                        {% else %}
                        <div></div>
                        {% endif %}

                        {% if tem_proxima %}
                        <a href="{{ url_proxima }}" class="btn-next">Próxima Lição »</a>
                        {% else %}
                        <a href="/discipulado/classe/{{ cid }}/avaliacao" class="btn btn-success fw-bold px-4 py-3 rounded-3 shadow">Fazer Avaliação da Classe 📝</a>
                        {% endif %}
                    </div>

                    <!-- Enviar Dúvida Vinculada a esta Lição Específica -->
                    <div class="card-duvida">
                        <h5 class="fw-bold mb-1" style="color: #0d3b66;">💬 Ficou com alguma dúvida nesta Lição?</h5>
                        <p class="text-muted small mb-3">A sua pergunta será direcionada ao professor associada à <b>Lição {{ licao_atual.numero }}: {{ licao_atual.titulo }}</b>.</p>
                        <form action="/discipulado/enviar_duvida" method="POST">
                            <input type="hidden" name="membro_id" value="{{ m_id }}">
                            <input type="hidden" name="membro_nome" value="{{ nome_membro }}">
                            <input type="hidden" name="classe_nome" value="{{ classe.nome }}">
                            <input type="hidden" name="licao_titulo" value="Lição {{ licao_atual.numero }}: {{ licao_atual.titulo }}">
                            <input type="hidden" name="url_origem" value="/discipulado/classe/{{ cid }}/licao/{{ lid }}">
                            <div class="mb-3">
                                <textarea name="duvida" rows="3" class="form-control" placeholder="Escreva aqui a sua dúvida bíblica ou doutrinária..." required></textarea>
                            </div>
                            <button type="submit" class="btn btn-outline-primary btn-sm fw-bold px-3 py-2">Enviar Pergunta ao Professor</button>
                        </form>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, classe=classe, cid=cid, lid=lid, licao_atual=licao_atual,
                                  tem_anterior=tem_anterior, tem_proxima=tem_proxima,
                                  url_anterior=url_anterior, url_proxima=url_proxima,
                                  total_licoes=total_licoes, bloqueada=bloqueada,
                                  concluiu_todas=concluiu_todas, m_id=m_id, nome_membro=nome_membro)

@app.route('/discipulado/enviar_duvida', methods=['POST'])
def enviar_duvida_licao():
    from flask import request, redirect
    m_id = request.form.get('membro_id', 1)
    m_nome = request.form.get('membro_nome', 'Aluno')
    c_nome = request.form.get('classe_nome', '')
    l_titulo = request.form.get('licao_titulo', '')
    duvida = request.form.get('duvida', '').strip()
    url_origem = request.form.get('url_origem', '/estudos')

    if duvida:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO duvidas_discipulado (membro_id, membro_nome, classe_nome, licao_titulo, duvida)
                VALUES (%s, %s, %s, %s, %s)
            """ if DATABASE_URL and psycopg2 else """
                INSERT INTO duvidas_discipulado (membro_id, membro_nome, classe_nome, licao_titulo, duvida)
                VALUES (?, ?, ?, ?, ?)
            """, (m_id, m_nome, c_nome, l_titulo, duvida))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao salvar duvida: {e}")

    return redirect(url_origem)

@app.route('/discipulado/classe/<cid>/avaliacao')
def ver_avaliacao_classe(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe não encontrada", 404

    classe = CURRICULO_CLASSES[cid]
    from flask import render_template_string
    html = """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="utf-8">
        <title>Avaliação: {{ classe.nome }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f1f5f9; font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; }
            .card-prova { border: none; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); background: white; overflow: hidden; }
            .card-header-prova { background: #0d3b66; color: white; padding: 22px; border-bottom: 4px solid #d4af37; }
        </style>
    </head>
    <body class="py-5">
        <div class="container" style="max-width: 800px;">
            <div class="card-prova">
                <div class="card-header-prova">
                    <h3 class="fw-bold mb-1">📝 Prova de Avaliação</h3>
                    <div class="text-light">{{ classe.nome }} • Questionário Oficial</div>
                </div>
                <div class="card-body p-4 p-md-5">
                    <form action="/discipulado/avaliar/{{ cid }}" method="POST">
                        <input type="hidden" name="membro_id" value="1">
                        {% for q in classe.questionario %}
                        <div class="mb-4 pb-3 border-bottom">
                            <p class="fw-bold text-dark mb-2" style="font-size: 1.05rem;">{{ loop.index }}. {{ q.pergunta }}</p>
                            {% for op in q.opcoes %}
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="resp_{{ q.id }}" value="{{ loop.index0 }}" id="q_{{ q.id }}_{{ loop.index0 }}" required>
                                <label class="form-check-label text-secondary" for="q_{{ q.id }}_{{ loop.index0 }}" style="font-size: 1rem;">{{ op }}</label>
                            </div>
                            {% endfor %}
                        </div>
                        {% endfor %}
                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="/discipulado/classe/{{ cid }}/licao/0" class="btn btn-outline-secondary">« Rever Lições</a>
                            <button type="submit" class="btn btn-primary fw-bold px-4 py-3 rounded-3 shadow">Submeter Respostas e Concluir Classe »</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, classe=classe, cid=cid)
'''

# Substitui a rota anterior de ver_classe_discipulado
if "def ver_classe_discipulado(cid):" in conteudo:
    partes = conteudo.split("def ver_classe_discipulado(cid):")
    topo = partes[0].rstrip()
    if topo.endswith("@app.route('/discipulado/classe/<cid>')"):
        topo = topo.rsplit("@app.route('/discipulado/classe/<cid>')", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + novo_bloco_licao_por_licao + "\n@app." + resto[1]
else:
    conteudo += "\n" + novo_bloco_licao_por_licao

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Fluxo lição a lição com botão Próximo e dúvidas específicas integrado com sucesso!")