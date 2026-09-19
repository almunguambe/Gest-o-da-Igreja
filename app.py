import os
import sqlite3
from datetime import datetime
import json
import io
import zipfile
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# ReportLab para PDFs
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "iead_chicuque_chave_super_segura_2026"
DB_NAME = "gestao_chicuque.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS membros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        genero TEXT,
        data_nascimento TEXT,
        faixa_etaria TEXT,
        naturalidade TEXT,
        bairro TEXT,
        filiacao TEXT,
        tipo_documento TEXT,
        numero_documento TEXT,
        ano_conversao INTEGER,
        data_batismo TEXT,
        posicao_atual TEXT,
        progressoes TEXT,
        departamento TEXT,
        foto_path TEXT,
        observacoes TEXT,
        data_registo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        local_movimento TEXT DEFAULT 'Caixa',
        departamento TEXT DEFAULT 'Geral',
        categoria TEXT NOT NULL,
        valor REAL NOT NULL,
        data_movimento TEXT NOT NULL,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        data_registo TEXT NOT NULL,
        membro_id INTEGER,
        descricao TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transferencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_movimento TEXT NOT NULL,
        origem_local TEXT NOT NULL,
        origem_depto TEXT NOT NULL,
        destino_local TEXT NOT NULL,
        destino_depto TEXT NOT NULL,
        valor REAL NOT NULL,
        motivo TEXT NOT NULL,
        data_registo TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS casamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        noivo TEXT NOT NULL,
        noiva TEXT NOT NULL,
        data_casamento TEXT NOT NULL,
        pastor_oficiante TEXT,
        data_registo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS mortes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_falecido TEXT NOT NULL,
        data_falecimento TEXT NOT NULL,
        observacoes TEXT,
        data_registo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS departamentos_lista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS categorias_financeiras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        nome TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS zonas_lista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_culto TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        homens INTEGER DEFAULT 0,
        mulheres INTEGER DEFAULT 0,
        jovens INTEGER DEFAULT 0,
        criancas INTEGER DEFAULT 0,
        visitantes INTEGER DEFAULT 0,
        novos_convertidos INTEGER DEFAULT 0,
        total_presentes INTEGER DEFAULT 0,
        pregador TEXT,
        tema_mensagem TEXT,
        data_registo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS novos_convertidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        bairro TEXT,
        data_decisao TEXT NOT NULL,
        culto_origem TEXT,
        quem_convidou TEXT,
        status_discipulado TEXT DEFAULT 'Decisão Inicial',
        observacoes TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS patrimonio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        departamento TEXT DEFAULT 'Geral',
        quantidade INTEGER DEFAULT 1,
        estado_conservacao TEXT DEFAULT 'Bom',
        localizacao TEXT,
        observacoes TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS escalas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_escala TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        dirigente TEXT,
        pregador TEXT,
        leitura_palavra TEXT,
        louvor_grupo TEXT,
        diaconos_servico TEXT,
        observacoes TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS campanhas_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_campanha TEXT NOT NULL,
        departamento TEXT DEFAULT 'Construção',
        valor_meta REAL NOT NULL,
        status TEXT DEFAULT 'Ativa'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        licao TEXT NOT NULL,
        nota INTEGER NOT NULL,
        total INTEGER NOT NULL,
        data_resposta TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS duvidas_estudantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        licao TEXT NOT NULL,
        duvida TEXT NOT NULL,
        resposta TEXT,
        data_envio TEXT NOT NULL
    )''')

    # Contas fixas e permanentes da congregação
    contas_permanentes = [
        ('admin', 'chicuque123', 'Pastor Presidente'),
        ('secretaria', '12345', 'Secretário'),
        ('tesouraria', 'senha12345', 'Tesoureiro'),
        ('doutrina', 'senha12345', 'Aluno')
    ]
    for usr, pwd, crg in contas_permanentes:
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (usr, pwd, crg))

    deptos = ['Activista', 'Juventude', 'Mulher (Senhoras)', 'Boa Esperança (Crianças)', 'Homens / Obreiros', 'Louvor / Música', 'Ação Social', 'Construção']
    for d in deptos:
        c.execute("INSERT OR IGNORE INTO departamentos_lista (nome) VALUES (?)", (d,))

    c.execute("SELECT COUNT(*) FROM categorias_financeiras")
    if c.fetchone()[0] == 0:
        padroes = [
            ('Entrada', 'Dízimo'), ('Entrada', 'Oferta'), ('Entrada', 'Doação / Voto'), ('Entrada', 'Campanha de Construção'),
            ('Saída', 'Manutenção do Templo'), ('Saída', 'Ação Social / Ajudas'), ('Saída', 'Combustível / Transporte'),
            ('Saída', 'Água e Eletricidade'), ('Saída', 'Material de Culto')
        ]
        c.executemany("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", padroes)

    zonas = ['Chicuque Sede', 'Maxixe Cidade', 'Nhacoongo', 'Conguiana', 'Bairro 1']
    for z in zonas:
        c.execute("INSERT OR IGNORE INTO zonas_lista (nome) VALUES (?)", (z,))

    c.execute("SELECT COUNT(*) FROM campanhas_metas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO campanhas_metas (nome_campanha, departamento, valor_meta, status) VALUES (?, ?, ?, ?)",
                  ('Campanha de Obras e Ampliação do Templo', 'Construção', 100000.0, 'Ativa'))

    conn.commit()
    conn.close()

init_db()

def is_admin():
    cargo = session.get('cargo', '')
    return session.get('usuario') == 'admin' or 'Pastor' in cargo

def can_cadastro():
    cargo = session.get('cargo', '')
    return is_admin() or 'Secretário' in cargo or 'Líder' in cargo

def can_tesouraria():
    cargo = session.get('cargo', '')
    return is_admin() or 'Tesoureiro' in cargo

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = (request.form.get('usuario') or '').strip()
        senha = (request.form.get('senha') or '').strip()
        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE LOWER(TRIM(usuario)) = LOWER(?) AND senha = ?", (usuario, senha)).fetchone()
        conn.close()
        if user:
            session['usuario'] = user['usuario']
            session['cargo'] = user['cargo']
            if user['cargo'] == 'Estudante':
                return redirect(url_for('portal_estudos'))
            return redirect(url_for('dashboard'))
        return render_template('login.html', erro="Utilizador ou palavra-passe incorretos.")
    return render_template('login.html', erro=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    if session.get('cargo') == 'Estudante':
        return redirect(url_for('portal_estudos'))

    conn = get_db()
    total_membros = conn.execute("SELECT COUNT(*) FROM membros").fetchone()[0]
    total_casamentos = conn.execute("SELECT COUNT(*) FROM casamentos").fetchone()[0]
    total_mortes = conn.execute("SELECT COUNT(*) FROM mortes").fetchone()[0]

    entrada_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saida_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saldo_caixa = entrada_caixa - saida_caixa

    entrada_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saida_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saldo_banco = entrada_banco - saida_banco
    saldo_total = (entrada_caixa + entrada_banco) - (saida_caixa + saida_banco)

    hoje_md = datetime.now().strftime("-%m-%d")
    aniversariantes_dia = conn.execute("SELECT nome, data_nascimento, telefone, departamento FROM membros WHERE data_nascimento LIKE ?", (f"%{hoje_md}",)).fetchall()

    campanhas_raw = conn.execute("SELECT * FROM campanhas_metas WHERE status = 'Ativa'").fetchall()
    campanhas = []
    for c in campanhas_raw:
        arrecadado = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND (categoria LIKE '%Construção%' OR departamento = ?)", (c['departamento'],)).fetchone()[0] or 0.0
        perc = min(round((arrecadado / c['valor_meta']) * 100, 1), 100) if c['valor_meta'] > 0 else 0
        campanhas.append({
            'id': c['id'], 'nome': c['nome_campanha'], 'meta': c['valor_meta'],
            'arrecadado': arrecadado, 'percentual': perc
        })

    ano_atual = datetime.now().year
    evolucao_entradas, evolucao_saidas = [], []
    for m in range(1, 13):
        e_mes = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND mes = ? AND ano = ?", (m, ano_atual)).fetchone()[0] or 0.0
        s_mes = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND mes = ? AND ano = ?", (m, ano_atual)).fetchone()[0] or 0.0
        evolucao_entradas.append(e_mes)
        evolucao_saidas.append(s_mes)

    deptos_lista = [d['nome'] for d in conn.execute("SELECT nome FROM departamentos_lista ORDER BY nome ASC").fetchall()]
    deptos_financeiro = ['Geral'] + [d for d in deptos_lista if d != 'Geral']
    depto_fin_labels, depto_fin_entradas, depto_fin_saidas = [], [], []
    for d in deptos_financeiro:
        ent = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND departamento = ?", (d,)).fetchone()[0] or 0.0
        sai = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND departamento = ?", (d,)).fetchone()[0] or 0.0
        if ent > 0 or sai > 0 or d in ['Geral', 'Activista', 'Juventude', 'Mulher (Senhoras)', 'Boa Esperança (Crianças)']:
            depto_fin_labels.append(d)
            depto_fin_entradas.append(ent)
            depto_fin_saidas.append(sai)

    fontes_rows = conn.execute("SELECT categoria, SUM(valor) as total FROM financeiro WHERE tipo = 'Entrada' GROUP BY categoria ORDER BY total DESC").fetchall()
    fontes_labels = [r['categoria'] for r in fontes_rows] if fontes_rows else ['Sem Entradas']
    fontes_valores = [r['total'] for r in fontes_rows] if fontes_rows else [0]

    saidas_rows = conn.execute("SELECT categoria, SUM(valor) as total FROM financeiro WHERE tipo = 'Saída' GROUP BY categoria ORDER BY total DESC").fetchall()
    saidas_labels = [r['categoria'] for r in saidas_rows] if saidas_rows else ['Sem Saídas']
    saidas_valores = [r['total'] for r in saidas_rows] if saidas_rows else [0]

    todos_membros = conn.execute("SELECT * FROM membros ORDER BY id DESC").fetchall()
    todas_financas = conn.execute("SELECT * FROM financeiro ORDER BY id DESC").fetchall()
    todos_casamentos = conn.execute("SELECT * FROM casamentos ORDER BY id DESC").fetchall()
    todas_mortes = conn.execute("SELECT * FROM mortes ORDER BY id DESC").fetchall()
    todos_cultos = conn.execute("SELECT * FROM cultos_frequencia ORDER BY id DESC LIMIT 25").fetchall()
    todos_convertidos = conn.execute("SELECT * FROM novos_convertidos ORDER BY id DESC").fetchall()
    todo_patrimonio = conn.execute("SELECT * FROM patrimonio ORDER BY departamento, item ASC").fetchall()
    todas_escalas = conn.execute("SELECT * FROM escalas ORDER BY data_escala DESC LIMIT 20").fetchall()
    lista_usuarios = conn.execute("SELECT id, usuario, cargo FROM usuarios ORDER BY id ASC").fetchall()
    ultimas_transferencias = conn.execute("SELECT * FROM transferencias ORDER BY id DESC LIMIT 20").fetchall()
    lista_avaliacoes = conn.execute("SELECT * FROM avaliacoes_estudantes ORDER BY id DESC").fetchall()
    todas_duvidas = conn.execute("SELECT * FROM duvidas_estudantes ORDER BY id DESC").fetchall()

    lista_deptos = conn.execute("SELECT * FROM departamentos_lista ORDER BY nome ASC").fetchall()
    lista_categorias = conn.execute("SELECT * FROM categorias_financeiras ORDER BY tipo, nome ASC").fetchall()
    lista_zonas = conn.execute("SELECT * FROM zonas_lista ORDER BY nome ASC").fetchall()

    categorias_json = json.dumps([{'tipo': c['tipo'], 'nome': c['nome']} for c in lista_categorias])
    membros_json = json.dumps([dict(m) for m in todos_membros])

    conn.close()

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)

    return render_template('dashboard.html',
                           pode_cadastro=can_cadastro(),
                           pode_tesouraria=can_tesouraria(),
                           e_admin=is_admin(),
                           alerta_duplicado=alerta_duplicado,
                           sucesso_cadastro=sucesso_cadastro,
                           total_membros=total_membros,
                           total_casamentos=total_casamentos,
                           total_mortes=total_mortes,
                           saldo_caixa=saldo_caixa,
                           saldo_banco=saldo_banco,
                           saldo_total=saldo_total,
                           aniversariantes_dia=aniversariantes_dia,
                           campanhas=campanhas,
                           todos_membros=todos_membros,
                           todas_financas=todas_financas,
                           todos_casamentos=todos_casamentos,
                           todas_mortes=todas_mortes,
                           todos_cultos=todos_cultos,
                           todos_convertidos=todos_convertidos,
                           todo_patrimonio=todo_patrimonio,
                           todas_escalas=todas_escalas,
                           lista_usuarios=lista_usuarios,
                           lista_avaliacoes=lista_avaliacoes,
                           todas_duvidas=todas_duvidas,
                           lista_deptos=lista_deptos,
                           lista_categorias=lista_categorias,
                           lista_zonas=lista_zonas,
                           ultimas_transferencias=ultimas_transferencias,
                           categorias_json=categorias_json,
                           membros_json=membros_json,
                           evolucao_entradas=json.dumps(evolucao_entradas),
                           evolucao_saidas=json.dumps(evolucao_saidas),
                           depto_fin_labels=json.dumps(depto_fin_labels),
                           depto_fin_entradas=json.dumps(depto_fin_entradas),
                           depto_fin_saidas=json.dumps(depto_fin_saidas),
                           fontes_labels=json.dumps(fontes_labels),
                           fontes_valores=json.dumps(fontes_valores),
                           saidas_labels=json.dumps(saidas_labels),
                           saidas_valores=json.dumps(saidas_valores))

@app.route('/estudos')
def portal_estudos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    resultado_teste = session.pop('resultado_teste', None)
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor="258866677810")


@app.route('/estudos/duvida', methods=['POST'])
def enviar_duvida():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session.get('usuario')
    licao = request.form.get('licao', 'Geral')
    duvida = request.form.get('duvida', '').strip()
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    if duvida:
        conn = get_db()
        param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
        conn.execute(f"INSERT INTO duvidas_estudantes (usuario, licao, duvida, data_envio) VALUES ({param_char}, {param_char}, {param_char}, {param_char})",
                     (usuario, licao, duvida, data_agora))
        conn.commit()
        conn.close()
        session['resultado_teste'] = "A sua dúvida foi enviada com sucesso à liderança pastoral!"
    
    return redirect(url_for('portal_estudos'))

@app.route('/estudos/responder', methods=['POST'])
def responder_estudos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    licao = request.form.get('licao', 'Geral')
    p1 = request.form.get('p1', '')
    p2 = request.form.get('p2', '')

    acertos = 0
    if p1 == 'B': acertos += 1
    if p2 == 'A': acertos += 1

    nota_final = int((acertos / 2) * 100)
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = get_db()
    conn.execute("INSERT INTO avaliacoes_estudantes (usuario, licao, nota, total, data_resposta) VALUES (?, ?, ?, ?, ?)",
                 (session['usuario'], licao, nota_final, 100, data_agora))
    conn.commit()
    conn.close()

    session['resultado_teste'] = f"Parabéns! Obteve {acertos} de 2 acertos ({nota_final}%) na avaliação."
    return redirect(url_for('portal_estudos'))

@app.route('/membros/novo', methods=['POST'])
def novo_membro():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    nome = request.form.get('nome', '').strip()
    num_doc = request.form.get('numero_documento', '').strip()
    tipo_doc = request.form.get('tipo_documento', 'BI')

    conn = get_db()
    if num_doc:
        existente_doc = conn.execute("SELECT id, nome FROM membros WHERE numero_documento = ? AND numero_documento != ''", (num_doc,)).fetchone()
        if existente_doc:
            conn.close()
            session['alerta_duplicado'] = f"Já existe membro com o documento nº {num_doc} ({existente_doc['nome']})."
            return redirect(url_for('dashboard'))

    existente_nome = conn.execute("SELECT id FROM membros WHERE LOWER(TRIM(nome)) = LOWER(?)", (nome,)).fetchone()
    if existente_nome:
        conn.close()
        session['alerta_duplicado'] = f"O membro '{nome}' já se encontra registado."
        return redirect(url_for('dashboard'))

    foto_path = ""
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and foto.filename:
            ext = foto.filename.rsplit('.', 1)[-1].lower()
            if ext in ['png', 'jpg', 'jpeg', 'webp']:
                nome_foto = f"membro_{int(datetime.now().timestamp())}.{ext}"
                salvar_em = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
                foto.save(salvar_em)
                foto_path = f"/static/uploads/{nome_foto}"

    ano_conv = request.form.get('ano_conversao')
    ano_conv_val = int(ano_conv) if ano_conv and ano_conv.isdigit() else None

    conn.execute('''
        INSERT INTO membros (
            nome, telefone, genero, data_nascimento, faixa_etaria,
            naturalidade, bairro, filiacao, tipo_documento, numero_documento,
            ano_conversao, data_batismo, posicao_atual, progressoes,
            departamento, foto_path, observacoes, data_registo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nome, request.form.get('telefone', '').strip(), request.form.get('genero', 'Masculino'),
        request.form.get('data_nascimento', ''), request.form.get('faixa_etaria', 'Adulto'),
        request.form.get('naturalidade', '').strip(), request.form.get('bairro', ''),
        request.form.get('filiacao', '').strip(), tipo_doc, num_doc, ano_conv_val,
        request.form.get('data_batismo', ''), request.form.get('posicao_atual', 'Membro em Comunhão'),
        request.form.get('progressoes', '').strip(), request.form.get('departamento', 'Geral'),
        foto_path, request.form.get('observacoes', '').strip(), datetime.now().strftime("%d/%m/%Y")
    ))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = f"Membro '{nome}' registado com sucesso!"
    return redirect(url_for('dashboard'))

@app.route('/cultos/novo', methods=['POST'])
def novo_culto():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    h = int(request.form.get('homens') or 0)
    m = int(request.form.get('mulheres') or 0)
    j = int(request.form.get('jovens') or 0)
    c = int(request.form.get('criancas') or 0)
    v = int(request.form.get('visitantes') or 0)
    nc = int(request.form.get('novos_convertidos') or 0)
    total = h + m + j + c + v

    conn = get_db()
    conn.execute('''INSERT INTO cultos_frequencia (data_culto, tipo_culto, homens, mulheres, jovens, criancas, visitantes, novos_convertidos, total_presentes, pregador, tema_mensagem, data_registo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['data_culto'], request.form['tipo_culto'], h, m, j, c, v, nc, total,
                  request.form.get('pregador', ''), request.form.get('tema_mensagem', ''), datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Culto e frequência registados!"
    return redirect(url_for('dashboard'))

@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute('''INSERT INTO novos_convertidos (nome, telefone, bairro, data_decisao, culto_origem, quem_convidou, status_discipulado, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['nome'].strip(), request.form.get('telefone', '').strip(), request.form.get('bairro', ''),
                  request.form['data_decisao'], request.form.get('culto_origem', ''), request.form.get('quem_convidou', ''),
                  request.form.get('status_discipulado', 'Decisão Inicial'), request.form.get('observacoes', '')))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Novo convertido registado!"
    return redirect(url_for('dashboard'))

@app.route('/convertidos/atualizar_status/<int:id>', methods=['POST'])
def atualizar_status_convertido(id):
    if not can_cadastro(): return redirect(url_for('dashboard'))
    novo_status = request.form.get('status_discipulado')
    conn = get_db()
    conn.execute("UPDATE novos_convertidos SET status_discipulado = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/patrimonio/novo', methods=['POST'])
def novo_patrimonio():
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute('''INSERT INTO patrimonio (item, departamento, quantidade, estado_conservacao, localizacao, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (request.form['item'].strip(), request.form.get('departamento', 'Geral'),
                  int(request.form.get('quantidade') or 1), request.form.get('estado_conservacao', 'Bom'),
                  request.form.get('localizacao', 'Templo Sede'), request.form.get('observacoes', '')))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Património registado!"
    return redirect(url_for('dashboard'))

@app.route('/escalas/novo', methods=['POST'])
def nova_escala():
    if not is_admin() and not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['data_escala'], request.form['tipo_culto'], request.form.get('dirigente', ''),
                  request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                  request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', '')))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Escala registada!"
    return redirect(url_for('dashboard'))

@app.route('/escalas/pdf/<int:id>')
def escala_pdf(id):
    conn = get_db()
    e = conn.execute("SELECT * FROM escalas WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not e: return redirect(url_for('dashboard'))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1)),
        Paragraph("<font color='#475569' size=9><b>CONGREGAÇÃO DE CHICUQUE • ESCALA OFICIAL DE CULTO</b></font>", ParagraphStyle('H2', alignment=1, spaceAfter=20)),
        Paragraph(f"<font color='#0f172a' size=14><b>ESCALA DE {e['tipo_culto'].upper()} — {e['data_escala']}</b></font>", ParagraphStyle('T', alignment=1, spaceAfter=20))
    ]
    dados = [
        ["Função Litúrgica", "Obreiro / Equipa Responsável"],
        ["Dirigente do Culto:", e['dirigente'] or 'A definir'],
        ["Ministração da Palavra (Pregador):", e['pregador'] or 'A definir'],
        ["Leitura Bíblica Inicial:", e['leitura_palavra'] or 'A definir'],
        ["Grupo de Louvor / Música:", e['louvor_grupo'] or 'Geral'],
        ["Diáconos / Serviço de Recepção:", e['diaconos_servico'] or 'A definir'],
        ["Notas Pastorais:", e['observacoes'] or 'Comparecer 30 minutos antes com traje solene.']
    ]
    t = Table(dados, colWidths=[7*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 2*cm))
    ass = [[
        Paragraph("____________________________________<br/><b>Secretaria / Direção de Culto</b>", ParagraphStyle('A1', alignment=1)),
        Paragraph("____________________________________<br/><b>Visto do Pastor Presidente</b>", ParagraphStyle('A2', alignment=1))
    ]]
    elementos.append(Table(ass, colWidths=[8*cm, 8*cm]))
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Escala_Culto_{e['data_escala']}.pdf", mimetype="application/pdf")

@app.route('/membro/cartao_pdf/<int:id>')
def cartao_membro_pdf(id):
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    m = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not m: return redirect(url_for('dashboard'))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(8.5*cm, 5.4*cm))
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, 0, 8.5*cm, 5.4*cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.rect(0, 4.2*cm, 8.5*cm, 1.2*cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#f59e0b"))
    c.rect(0, 4.15*cm, 8.5*cm, 0.06*cm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(4.25*cm, 4.85*cm, "IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS")
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.HexColor("#93c5fd"))
    c.drawCentredString(4.25*cm, 4.45*cm, "CONGREGAÇÃO DE CHICUQUE • CARTÃO DE MEMBRO")

    c.setFillColor(colors.white)
    c.roundRect(0.5*cm, 1.2*cm, 2.0*cm, 2.6*cm, 3, fill=1, stroke=1)
    
    foto_desenhada = False
    if m['foto_path']:
        caminho_real = m['foto_path'].lstrip('/')
        if os.path.exists(caminho_real):
            try:
                c.drawImage(caminho_real, 0.55*cm, 1.25*cm, width=1.9*cm, height=2.5*cm, preserveAspectRatio=True)
                foto_desenhada = True
            except Exception: pass
            
    if not foto_desenhada:
        c.setFillColor(colors.HexColor("#1e3a8a"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(1.5*cm, 2.3*cm, m['nome'][:2].upper())

    c.setFillColor(colors.HexColor("#f8fafc"))
    c.setFont("Helvetica-Bold", 8.5)
    nome_curto = m['nome'] if len(m['nome']) <= 25 else m['nome'][:23] + "..."
    c.drawString(2.8*cm, 3.5*cm, nome_curto)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(colors.HexColor("#fbbf24"))
    c.drawString(2.8*cm, 3.1*cm, f"CARGO: {m['posicao_atual'] or 'Membro'}")
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.drawString(2.8*cm, 2.65*cm, f"Ministério: {m['departamento'] or 'Geral'}")
    c.drawString(2.8*cm, 2.25*cm, f"Doc: {m['tipo_documento'] or 'BI'} - {m['numero_documento'] or 'S/N'}")
    c.drawString(2.8*cm, 1.85*cm, f"Batismo: {m['data_batismo'] or '-'} | Conv: {m['ano_conversao'] or '-'}")
    c.drawString(2.8*cm, 1.45*cm, f"Bairro/Zona: {m['bairro'] or 'Chicuque'}")

    c.setFont("Helvetica", 5)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(0.5*cm, 0.4*cm, f"ID #{m['id']} • Válido com carimbo pastoral")
    c.drawRightString(8.0*cm, 0.4*cm, "Pastor Presidente")
    c.setStrokeColor(colors.HexColor("#475569"))
    c.line(5.5*cm, 0.65*cm, 8.0*cm, 0.65*cm)

    c.showPage()
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Cartao_Membro_{m['nome'].replace(' ', '_')}.pdf", mimetype="application/pdf")

@app.route('/membro/certificado_pdf/<int:id>/<tipo>')
def certificado_membro_pdf(id, tipo):
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    m = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not m: return redirect(url_for('dashboard'))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    titulo_cert = {
        'batismo': "CERTIFICADO DE BATISMO NAS ÁGUAS",
        'apresentacao': "CERTIFICADO DE APRESENTAÇÃO AO SENHOR",
        'recomendacao': "CARTA DE RECOMENDAÇÃO PASTORAL"
    }.get(tipo, "CERTIFICADO ECLESIÁSTICO")

    versiculo = {
        'batismo': '"Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo." — Mateus 28:19',
        'apresentacao': '"Deixai vir a mim os pequeninos e não os impeçais, porque dos tais é o Reino de Deus." — Marcos 10:14',
        'recomendacao': '"Recomendo-vos a nossa irmã, que vos seja apresentada no Senhor de um modo digno dos santos." — Romanos 16:1-2'
    }.get(tipo, '')

    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1, spaceAfter=4)),
        Paragraph("<font color='#475569' size=10><b>CONGREGAÇÃO DE CHICUQUE • INHAMBANE, MOÇAMBIQUE</b></font>", ParagraphStyle('H2', alignment=1, spaceAfter=15)),
        Spacer(1, 0.5*cm),
        Paragraph(f"<font color='#d97706' size=20><b>{titulo_cert}</b></font>", ParagraphStyle('T', alignment=1, spaceAfter=20))
    ]

    if tipo == 'batismo':
        corpo = f"Certificamos que <b>{m['nome'].upper()}</b>, nascido(a) em <b>{m['data_nascimento'] or '---'}</b>, natural de <b>{m['naturalidade'] or 'Moçambique'}</b>, portador(a) do documento <b>{m['tipo_documento'] or 'BI'} nº {m['numero_documento'] or '---'}</b>, desceu às águas batismais no dia <b>{m['data_batismo'] or datetime.now().strftime('%d/%m/%Y')}</b>, confessando publicamente a Jesus Cristo como seu Salvador."
    elif tipo == 'apresentacao':
        corpo = f"Certificamos que a criança <b>{m['nome'].upper()}</b>, nascida aos <b>{m['data_nascimento'] or '---'}</b>, filha de <b>{m['filiacao'] or 'seus pais'}</b>, foi solenemente apresentada a Deus nesta congregação, nos termos da Palavra Sagrada, sob oração e bênção pastoral."
    else:
        corpo = f"Pela presente recomendamos o(a) nosso(a) irmão(ã) em Cristo <b>{m['nome'].upper()}</b>, que congregou connosco em plena comunhão fraterna como <b>{m['posicao_atual']}</b>, prestando serviços no departamento <b>{m['departamento']}</b>. Rogamos que seja acolhido(a) no amor fraterno pelo vosso ministério."

    elementos.append(Paragraph(f"<font color='#1e293b' size=13 leading=22>{corpo}</font>", ParagraphStyle('B', alignment=4, spaceAfter=25)))
    elementos.append(Paragraph(f"<i><font color='#64748b' size=10>{versiculo}</font></i>", ParagraphStyle('V', alignment=1, spaceAfter=35)))
    elementos.append(Spacer(1, 1*cm))
    elementos.append(Paragraph(f"<font color='#334155' size=10><b>Chicuque, aos {datetime.now().strftime('%d de %B de %Y')}.</b></font>", ParagraphStyle('D', alignment=1, spaceAfter=30)))

    ass = [[
        Paragraph("_______________________________________<br/><b>Pastor Presidente da IEAD Chicuque</b>", ParagraphStyle('Ass1', alignment=1)),
        Paragraph("_______________________________________<br/><b>Secretaria Geral / Ministro Oficiante</b>", ParagraphStyle('Ass2', alignment=1))
    ]]
    elementos.append(Table(ass, colWidths=[12*cm, 12*cm]))
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Certificado_{tipo}_{m['nome'].replace(' ', '_')}.pdf", mimetype="application/pdf")

@app.route('/financeiro/recibo_pdf/<int:id>')
def recibo_financeiro_pdf(id):
    if not can_tesouraria(): return redirect(url_for('dashboard'))
    conn = get_db()
    f = conn.execute("SELECT * FROM financeiro WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not f: return redirect(url_for('dashboard'))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1)),
        Paragraph("<font color='#475569' size=9><b>CONGREGAÇÃO DE CHICUQUE • DEPARTAMENTO DE TESOURARIA</b></font>", ParagraphStyle('H2', alignment=1, spaceAfter=20)),
        Paragraph(f"<font color='#059669' size=16><b>COMPROVATIVO DE MOVIMENTO DE CAIXA Nº #{f['id']}</b></font>", ParagraphStyle('T', alignment=1, spaceAfter=20))
    ]
    dados = [
        ["Data do Movimento:", f['data_movimento']],
        ["Tipo de Operação:", f['tipo']],
        ["Conta / Caixa:", f['local_movimento']],
        ["Departamento / Fundo:", f['departamento'] or 'Geral'],
        ["Categoria / Área:", f['categoria']],
        ["Valor Registado:", f"{f['valor']:,.2f} MT"],
        ["Descrição / Finalidade:", f['descricao']],
        ["Data do Registo:", f['data_registo']]
    ]
    t = Table(dados, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#1e3a8a")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 2*cm))
    ass = [[
        Paragraph("____________________________________<br/><b>Responsável da Tesouraria</b>", ParagraphStyle('A1', alignment=1)),
        Paragraph("____________________________________<br/><b>Visto Pastoral / Controlo</b>", ParagraphStyle('A2', alignment=1))
    ]]
    elementos.append(Table(ass, colWidths=[8*cm, 8*cm]))
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Recibo_Caixa_{f['id']}.pdf", mimetype="application/pdf")

@app.route('/financeiro/balancete_pdf')
def balancete_financeiro_pdf():
    if not can_tesouraria(): return redirect(url_for('dashboard'))
    conn = get_db()
    entrada_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saida_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saldo_caixa = entrada_caixa - saida_caixa

    entrada_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saida_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saldo_banco = entrada_banco - saida_banco
    saldo_total = (entrada_caixa + entrada_banco) - (saida_caixa + saida_banco)

    movimentos = conn.execute("SELECT data_movimento, tipo, local_movimento, departamento, categoria, valor FROM financeiro ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1)),
        Paragraph("<font color='#475569' size=9><b>CONGREGAÇÃO DE CHICUQUE • BALANCETE FINANCEIRO CONSOLIDADO</b></font>", ParagraphStyle('H2', alignment=1, spaceAfter=15))
    ]
    resumo = [
        ["Conta / Caixa", "Entradas Totais", "Saídas Totais", "Saldo Atual"],
        ["Caixa Físico", f"{entrada_caixa:,.2f} MT", f"{saida_caixa:,.2f} MT", f"{saldo_caixa:,.2f} MT"],
        ["Conta Bancária", f"{entrada_banco:,.2f} MT", f"{saida_banco:,.2f} MT", f"{saldo_banco:,.2f} MT"],
        ["TOTAL GERAL", f"{entrada_caixa+entrada_banco:,.2f} MT", f"{saida_caixa+saida_banco:,.2f} MT", f"{saldo_total:,.2f} MT"]
    ]
    t_res = Table(resumo, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
    ]))
    elementos.append(t_res)
    elementos.append(Spacer(1, 1*cm))

    elementos.append(Paragraph("<b>EXTRATO DE LANÇAMENTOS RECENTES</b>", ParagraphStyle('H3', spaceAfter=8)))
    linhas = [["Data", "Tipo", "Conta", "Departamento", "Categoria", "Valor (MT)"]]
    for m in movimentos:
        linhas.append([m['data_movimento'], m['tipo'], m['local_movimento'], m['departamento'], m['categoria'], f"{m['valor']:,.2f}"])
    
    t_mov = Table(linhas, colWidths=[2.5*cm, 2*cm, 2.5*cm, 3.5*cm, 4.5*cm, 3*cm])
    t_mov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elementos.append(t_mov)
    elementos.append(Spacer(1, 1.5*cm))

    ass = [[
        Paragraph("____________________________<br/><b>1º Tesoureiro</b>", ParagraphStyle('A1', alignment=1)),
        Paragraph("____________________________<br/><b>Conselho Fiscal</b>", ParagraphStyle('A2', alignment=1)),
        Paragraph("____________________________<br/><b>Pastor Presidente</b>", ParagraphStyle('A3', alignment=1))
    ]]
    elementos.append(Table(ass, colWidths=[6*cm, 6*cm, 6*cm]))
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Balancete_IEAD_Chicuque_{datetime.now().strftime('%Y_%m')}.pdf", mimetype="application/pdf")

@app.route('/sistema/backup')
def backup_sistema():
    if not is_admin(): return redirect(url_for('dashboard'))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(DB_NAME):
            zipf.write(DB_NAME, arcname=DB_NAME)
        for root, _, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                caminho = os.path.join(root, file)
                rel_path = os.path.relpath(caminho, start=".")
                zipf.write(caminho, arcname=rel_path)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"BACKUP_COMPLETO_IEAD_CHICUQUE_{datetime.now().strftime('%Y%m%d_%H%M')}.zip", mimetype="application/zip")

@app.route('/financeiro/novo', methods=['POST'])
def novo_financeiro():
    if not can_tesouraria(): return redirect(url_for('dashboard'))
    data_raw = request.form.get('data_movimento') or datetime.now().strftime("%Y-%m-%d")
    dt_obj = datetime.strptime(data_raw, "%Y-%m-%d")
    conn = get_db()
    conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                  request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                  datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/financeiro/transferir', methods=['POST'])
def transferir_fundos():
    if not can_tesouraria(): return redirect(url_for('dashboard'))
    data_raw = request.form.get('data_movimento') or datetime.now().strftime("%Y-%m-%d")
    dt_obj = datetime.strptime(data_raw, "%Y-%m-%d")
    origem_local, origem_depto = request.form['origem_local'], request.form['origem_depto']
    destino_local, destino_depto = request.form['destino_local'], request.form['destino_depto']
    valor = float(request.form['valor'])
    motivo = request.form['motivo']
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = get_db()
    conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, descricao)
                    VALUES ('Saída', ?, ?, 'Transferência de Fundos', ?, ?, ?, ?, ?, ?, ?)''',
                 (origem_local, origem_depto, valor, dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year, agora, f"Transf. p/ [{destino_local} - {destino_depto}]: {motivo}"))
    conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, descricao)
                    VALUES ('Entrada', ?, ?, 'Transferência de Fundos', ?, ?, ?, ?, ?, ?, ?)''',
                 (destino_local, destino_depto, valor, dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year, agora, f"Transf. de [{origem_local} - {origem_depto}]: {motivo}"))
    conn.execute('''INSERT INTO transferencias (data_movimento, origem_local, origem_depto, destino_local, destino_depto, valor, motivo, data_registo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (dt_obj.strftime("%d/%m/%Y"), origem_local, origem_depto, destino_local, destino_depto, valor, motivo, agora))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/casamentos/novo', methods=['POST'])
def novo_casamento():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute('''INSERT INTO casamentos (noivo, noiva, data_casamento, pastor_oficiante, data_registo)
                    VALUES (?, ?, ?, ?, ?)''',
                 (request.form['noivo'], request.form['noiva'], request.form['data_casamento'],
                  request.form.get('pastor_oficiante', ''), datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/mortes/novo', methods=['POST'])
def novo_morte():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute('''INSERT INTO mortes (nome_falecido, data_falecimento, observacoes, data_registo)
                    VALUES (?, ?, ?, ?)''',
                 (request.form['nome_falecido'], request.form['data_falecimento'],
                  request.form.get('observacoes', ''), datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/usuarios/novo', methods=['POST'])
def novo_usuario():
    if not is_admin(): return redirect(url_for('dashboard'))
    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    if user and senha:
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (user, senha, cargo))
            conn.commit()
            session['sucesso_cadastro'] = f"Utilizador '{user}' criado com sucesso!"
        except Exception:
            session['alerta_duplicado'] = f"Utilizador '{user}' já existe."
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/usuarios/apagar/<int:id>')
def apagar_usuario(id):
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    u = conn.execute("SELECT usuario FROM usuarios WHERE id = ?", (id,)).fetchone()
    if u and u['usuario'] != 'admin':
        conn.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/apagar/<tabela>/<int:id>')
def apagar_registo(tabela, id):
    if not is_admin(): return redirect(url_for('dashboard'))
    mapa = {'membro': ('membros', 'id'), 'financeiro': ('financeiro', 'id'), 'casamento': ('casamentos', 'id'), 'morte': ('mortes', 'id'), 'patrimonio': ('patrimonio', 'id'), 'escala': ('escalas', 'id'), 'culto': ('cultos_frequencia', 'id'), 'convertido': ('novos_convertidos', 'id')}
    if tabela in mapa:
        tab, col = mapa[tabela]
        conn = get_db()
        conn.execute(f"DELETE FROM {tab} WHERE {col} = ?", (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/departamento/novo', methods=['POST'])
def novo_depto():
    if not is_admin(): return redirect(url_for('dashboard'))
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO departamentos_lista (nome) VALUES (?)", (nome,))
            conn.commit()
        except Exception: pass
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/departamento/apagar/<int:id>')
def apagar_depto(id):
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute("DELETE FROM departamentos_lista WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/categoria/novo', methods=['POST'])
def nova_categoria():
    if not is_admin(): return redirect(url_for('dashboard'))
    tipo, nome = request.form.get('tipo'), request.form.get('nome', '').strip()
    if tipo and nome:
        conn = get_db()
        conn.execute("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", (tipo, nome))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/categoria/apagar/<int:id>')
def apagar_categoria(id):
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute("DELETE FROM categorias_financeiras WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/zona/novo', methods=['POST'])
def nova_zona():
    if not is_admin(): return redirect(url_for('dashboard'))
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO zonas_lista (nome) VALUES (?)", (nome,))
            conn.commit()
        except Exception: pass
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/config/zona/apagar/<int:id>')
def apagar_zona(id):
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute("DELETE FROM zonas_lista WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/exportar/financeiro')
def exportar_financeiro():
    if not can_tesouraria(): return redirect(url_for('dashboard'))
    conn = get_db()
    rows = conn.execute("SELECT data_movimento, tipo, local_movimento, departamento, categoria, descricao, valor FROM financeiro ORDER BY id DESC").fetchall()
    conn.close()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tesouraria Chicuque"
    ws.append(["Data Movimento", "Tipo", "Conta", "Departamento", "Categoria", "Descrição", "Valor (MT)"])
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    for col in range(1, 8):
        c = ws.cell(row=1, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")
    for r in rows:
        ws.append([r['data_movimento'], r['tipo'], r['local_movimento'], r['departamento'], r['categoria'], r['descricao'], r['valor']])
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Tesouraria_IEAD_Chicuque_{datetime.now().strftime('%Y%m%d')}.xlsx")

@app.route('/exportar/membros')
def exportar_membros():
    if not can_cadastro(): return redirect(url_for('dashboard'))
    conn = get_db()
    rows = conn.execute('''
        SELECT nome, telefone, genero, data_nascimento, faixa_etaria, naturalidade, bairro, 
               filiacao, tipo_documento, numero_documento, ano_conversao, data_batismo, 
               posicao_atual, progressoes, departamento, observacoes
        FROM membros ORDER BY nome ASC
    ''').fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Membresia IEAD Chicuque"
    headers = [
        "Nome Completo", "Contacto", "Género", "Data Nasc.", "Segmento", "Naturalidade", "Bairro",
        "Filiação", "Tipo Doc", "Nº Documento", "Ano Conv.", "Data Batismo",
        "Posição Atual", "Progressões", "Departamento", "Observações"
    ]
    ws.append(headers)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    for col in range(1, len(headers) + 1):
        c = ws.cell(row=1, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")
    for r in rows:
        ws.append([r[k] for k in r.keys()])
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 13)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Membros_Completos_IEAD_{datetime.now().strftime('%Y%m%d')}.xlsx")


@app.route('/estudos/duvidas/responder/<int:id>', methods=['POST'])
def responder_duvida_pastor(id):
    if not (is_admin() or can_cadastro()):
        return redirect(url_for('dashboard'))
    
    resposta = request.form.get('resposta', '').strip()
    if resposta:
        conn = get_db()
        param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
        conn.execute(f"UPDATE duvidas_estudantes SET resposta = {param_char} WHERE id = {param_char}", (resposta, id))
        conn.commit()
        conn.close()
        session['sucesso_cadastro'] = "Resposta pastoral enviada com sucesso para a sala de aula do aluno!"
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
