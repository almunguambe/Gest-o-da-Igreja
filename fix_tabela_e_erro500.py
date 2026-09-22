with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Função para assegurar a tabela progresso_discipulado na inicialização do Flask
bloco_auto_tabela = '''
def inicializar_tabela_discipulado():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        if DATABASE_URL and psycopg2:
            c.execute("""
                CREATE TABLE IF NOT EXISTS progresso_discipulado (
                    id SERIAL PRIMARY KEY,
                    membro_id INTEGER NOT NULL,
                    classe_id VARCHAR(10) NOT NULL,
                    nota NUMERIC(4,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'Pendente',
                    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS progresso_discipulado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membro_id INTEGER NOT NULL,
                    classe_id TEXT NOT NULL,
                    nota REAL DEFAULT 0,
                    status TEXT DEFAULT 'Pendente',
                    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso ao inicializar tabela discipulado: {e}")

try:
    inicializar_tabela_discipulado()
except Exception:
    pass
'''

if "def inicializar_tabela_discipulado():" not in conteudo:
    # Insere logo após a criação da função get_db_connection
    if "def get_db_connection():" in conteudo:
        partes = conteudo.split("def get_db_connection():")
        corpo = partes[1].split("\n@app.", 1)
        conteudo = partes[0] + "def get_db_connection():" + corpo[0] + "\n" + bloco_auto_tabela + "\n@app." + corpo[1]

# 2. Corrigir a rota ver_classe_discipulado para tratar banco sem membros ou erros de consulta
bloco_rota_segura = '''@app.route('/discipulado/classe/<cid>')
def ver_classe_discipulado(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe não encontrada", 404

    classe = CURRICULO_CLASSES[cid]
    aprovadas = set()
    m_id = 1

    try:
        conn = get_db_connection()
        c = conn.cursor()
        # Assegurar tabela caso ainda não tenha sido executada
        c.execute("""
            CREATE TABLE IF NOT EXISTS progresso_discipulado (
                id SERIAL PRIMARY KEY,
                membro_id INTEGER NOT NULL,
                classe_id VARCHAR(10) NOT NULL,
                nota NUMERIC(4,2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'Pendente',
                data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """ if DATABASE_URL and psycopg2 else """
            CREATE TABLE IF NOT EXISTS progresso_discipulado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER NOT NULL,
                classe_id TEXT NOT NULL,
                nota REAL DEFAULT 0,
                status TEXT DEFAULT 'Pendente',
                data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        c.execute("SELECT id, nome FROM membros ORDER BY id ASC LIMIT 1")
        membro = c.fetchone()
        if membro:
            if hasattr(membro, 'keys') and 'id' in membro.keys():
                m_id = membro['id']
            elif isinstance(membro, dict) and 'id' in membro:
                m_id = membro['id']
            else:
                m_id = membro[0]

        c.execute("SELECT classe_id, nota, status FROM progresso_discipulado WHERE membro_id = %s" if DATABASE_URL and psycopg2 else "SELECT classe_id, nota, status FROM progresso_discipulado WHERE membro_id = ?", (m_id,))
        registos = c.fetchall()
        conn.close()

        for r in registos:
            c_id = r['classe_id'] if hasattr(r, 'keys') else (r[0] if isinstance(r, (list, tuple)) else getattr(r, 'classe_id', ''))
            st = r['status'] if hasattr(r, 'keys') else (r[2] if isinstance(r, (list, tuple)) else getattr(r, 'status', ''))
            if st == 'Aprovado':
                aprovadas.add(str(c_id).strip())
    except Exception as err:
        print(f"Erro ao verificar progresso: {err}")

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
        <title>{{ classe.nome }} - IEAD Chicuque</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8fafc; font-family: 'Segoe UI', sans-serif; color: #1e293b; }
            .card-aula { border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); background: #ffffff; }
            .card-header-aula { background: #0d3b66; color: white; border-radius: 12px 12px 0 0; padding: 14px 20px; font-weight: 700; font-size: 1.05rem; }
            .badge-ouro { background: #d4af37; color: #0d3b66; font-weight: 700; font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; }
            .conteudo-licao { font-size: 1.02rem; line-height: 1.75; color: #334155; }
        </style>
    </head>
    <body class="p-3 p-md-5">
        <div class="container" style="max-width: 900px;">
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2 pb-3 border-bottom">
                <div>
                    <h2 class="fw-bold mb-1" style="color: #0d3b66;">{{ classe.nome }}</h2>
                    <span class="text-muted fw-semibold">{{ classe.duracao }} • Manual Oficial de Discipulado</span>
                </div>
                <div class="d-flex gap-2">
                    <a href="/" class="btn btn-outline-secondary">← Painel Principal</a>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-success fw-bold">🎓 Emitir Certificado de Conclusão</a>
                    {% endif %}
                </div>
            </div>

            <div class="d-flex gap-2 mb-4 overflow-auto pb-2">
                <a href="/discipulado/classe/c1" class="btn {% if cid == 'c1' %}btn-primary{% else %}btn-light border{% endif %} fw-semibold">Classe I {% if 'c1' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c2" class="btn {% if cid == 'c2' %}btn-primary{% else %}btn-light border{% endif %} fw-semibold">Classe II {% if 'c2' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c3" class="btn {% if cid == 'c3' %}btn-primary{% else %}btn-light border{% endif %} fw-semibold">Classe III {% if 'c3' in aprovadas %}✓{% endif %}</a>
                <a href="/discipulado/classe/c4" class="btn {% if cid == 'c4' %}btn-primary{% else %}btn-light border{% endif %} fw-semibold">Classe IV {% if 'c4' in aprovadas %}✓{% endif %}</a>
            </div>

            {% if bloqueada %}
            <div class="alert alert-warning p-4 rounded-4 shadow-sm text-center">
                <h4 class="fw-bold text-dark mb-2">Classe Bloqueada 🔒</h4>
                <p class="mb-0 text-secondary">Para ter acesso a esta classe, é necessário primeiro responder ao questionário da classe anterior e obter aprovação com nota mínima de 70%.</p>
            </div>
            {% else %}
                <h4 class="fw-bold mb-3" style="color: #0d3b66;">Conteúdo Integral das Lições</h4>
                {% for lic in classe.licoes %}
                <div class="card card-aula">
                    <div class="card-header card-header-aula d-flex justify-content-between align-items-center flex-wrap gap-2">
                        <span>Lição {{ lic.numero }}: {{ lic.titulo }}</span>
                        {% if lic.versiculo %}
                        <span class="badge badge-ouro">{{ lic.versiculo }}</span>
                        {% endif %}
                    </div>
                    <div class="card-body p-4">
                        <div class="conteudo-licao">{{ lic.conteudo | safe }}</div>
                    </div>
                </div>
                {% endfor %}

                <div class="card border-0 shadow-sm rounded-4 mt-5">
                    <div class="card-header bg-dark text-white p-3 px-4 rounded-top-4">
                        <h5 class="mb-0 fw-bold">📝 Questionário de Avaliação — {{ classe.nome }}</h5>
                        <small class="text-light">Responda às questões com atenção para desbloquear a classe seguinte.</small>
                    </div>
                    <div class="card-body p-4">
                        <form action="/discipulado/avaliar/{{ cid }}" method="POST">
                            <input type="hidden" name="membro_id" value="{{ m_id }}">
                            {% for q in classe.questionario %}
                            <div class="mb-4 pb-3 border-bottom">
                                <p class="fw-bold text-dark mb-2">{{ loop.index }}. {{ q.pergunta }}</p>
                                {% for op in q.opcoes %}
                                <div class="form-check mb-2">
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
'''

# Substitui a rota existente no app.py
if "def ver_classe_discipulado(cid):" in conteudo:
    partes = conteudo.split("def ver_classe_discipulado(cid):")
    topo = partes[0].rstrip()
    if topo.endswith("@app.route('/discipulado/classe/<cid>')"):
        topo = topo.rsplit("@app.route('/discipulado/classe/<cid>')", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + bloco_rota_segura + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Criação automática de tabelas e proteção contra erro 500 aplicadas!")