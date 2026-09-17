from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
from datetime import datetime
import json
import io
import os
from werkzeug.utils import secure_filename
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

app = Flask(__name__)
app.secret_key = "iead_chicuque_chave_super_segura_2026"
DB_NAME = "gestao_chicuque.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL
    )''')
    if c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                  ('admin', 'chicuque123', 'Pastor Presidente'))

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

    c.execute("PRAGMA table_info(membros)")
    cols = [col[1] for col in c.fetchall()]
    novas = [
        ('genero', 'TEXT'), ('data_nascimento', 'TEXT'), ('faixa_etaria', 'TEXT'),
        ('naturalidade', 'TEXT'), ('filiacao', 'TEXT'), ('tipo_documento', 'TEXT'),
        ('numero_documento', 'TEXT'), ('ano_conversao', 'INTEGER'), ('posicao_atual', 'TEXT'),
        ('progressoes', 'TEXT'), ('foto_path', 'TEXT')
    ]
    for n, t in novas:
        if n not in cols:
            c.execute(f"ALTER TABLE membros ADD COLUMN {n} {t}")

    c.execute('''CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT CHECK(tipo IN ('Entrada', 'Saída')),
        local_movimento TEXT CHECK(local_movimento IN ('Caixa', 'Banco')) DEFAULT 'Caixa',
        departamento TEXT DEFAULT 'Geral',
        categoria TEXT NOT NULL,
        valor REAL NOT NULL,
        data_movimento TEXT NOT NULL,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        data_registo TEXT NOT NULL,
        membro_id INTEGER,
        descricao TEXT,
        FOREIGN KEY (membro_id) REFERENCES membros (id)
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
        tipo TEXT CHECK(tipo IN ('Entrada', 'Saída')) NOT NULL,
        nome TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS zonas_lista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )''')

    deptos = [
        ('Activista',), ('Juventude',), ('Mulher (Senhoras)',), 
        ('Boa Esperança (Crianças)',), ('Homens / Obreiros',), 
        ('Louvor / Música',), ('Ação Social',), ('Construção',)
    ]
    for d in deptos:
        c.execute("INSERT OR IGNORE INTO departamentos_lista (nome) VALUES (?)", d)

    if c.execute("SELECT COUNT(*) FROM categorias_financeiras").fetchone()[0] == 0:
        padroes = [
            ('Entrada', 'Dízimo'), ('Entrada', 'Oferta'), ('Entrada', 'Doação / Voto'), ('Entrada', 'Campanha de Construção'),
            ('Saída', 'Manutenção do Templo'), ('Saída', 'Ação Social / Ajudas'), ('Saída', 'Combustível / Transporte'),
            ('Saída', 'Água e Eletricidade'), ('Saída', 'Material de Culto')
        ]
        c.executemany("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", padroes)

    if c.execute("SELECT COUNT(*) FROM zonas_lista").fetchone()[0] == 0:
        c.executemany("INSERT INTO zonas_lista (nome) VALUES (?)",
                      [('Chicuque Sede',), ('Maxixe Cidade',), ('Nhacoongo',), ('Conguiana',), ('Bairro 1',)])

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

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
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        conn = get_db()
        user = conn.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha)).fetchone()
        conn.close()
        if user:
            session['usuario'] = user['usuario']
            session['cargo'] = user['cargo']
            return redirect(url_for('dashboard'))
        return render_template('login.html', erro="Credenciais incorretas.")
    return render_template('login.html', erro=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
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

    # 1. Evolução Mensal Geral
    ano_atual = datetime.now().year
    evolucao_entradas, evolucao_saidas = [], []
    for m in range(1, 13):
        e_mes = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND mes = ? AND ano = ?", (m, ano_atual)).fetchone()[0] or 0.0
        s_mes = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND mes = ? AND ano = ?", (m, ano_atual)).fetchone()[0] or 0.0
        evolucao_entradas.append(e_mes)
        evolucao_saidas.append(s_mes)

    # 2. Situação Financeira por Departamento (Entradas vs Saídas)
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

    # 3. Fontes de Fundos (Entradas por Categoria)
    fontes_rows = conn.execute('''
        SELECT categoria, SUM(valor) as total 
        FROM financeiro 
        WHERE tipo = 'Entrada' 
        GROUP BY categoria 
        ORDER BY total DESC
    ''').fetchall()
    fontes_labels = [r['categoria'] for r in fontes_rows] if fontes_rows else ['Sem Entradas']
    fontes_valores = [r['total'] for r in fontes_rows] if fontes_rows else [0]

    # 4. Destino de Saídas (Despesas por Categoria)
    saidas_rows = conn.execute('''
        SELECT categoria, SUM(valor) as total 
        FROM financeiro 
        WHERE tipo = 'Saída' 
        GROUP BY categoria 
        ORDER BY total DESC
    ''').fetchall()
    saidas_labels = [r['categoria'] for r in saidas_rows] if saidas_rows else ['Sem Saídas']
    saidas_valores = [r['total'] for r in saidas_rows] if saidas_rows else [0]

    # Membros por departamento
    dept_rows = conn.execute("SELECT COALESCE(NULLIF(TRIM(departamento), ''), 'Geral') as dep, COUNT(*) as qtd FROM membros GROUP BY dep").fetchall()
    depto_labels = [r['dep'] for r in dept_rows] if dept_rows else ['Geral']
    depto_valores = [r['qtd'] for r in dept_rows] if dept_rows else [0]

    todos_membros = conn.execute("SELECT * FROM membros ORDER BY id DESC").fetchall()
    todas_financas = conn.execute("SELECT * FROM financeiro ORDER BY id DESC").fetchall()
    todos_casamentos = conn.execute("SELECT * FROM casamentos ORDER BY id DESC").fetchall()
    todas_mortes = conn.execute("SELECT * FROM mortes ORDER BY id DESC").fetchall()
    lista_usuarios = conn.execute("SELECT id, usuario, cargo FROM usuarios ORDER BY id ASC").fetchall()
    ultimas_transferencias = conn.execute("SELECT * FROM transferencias ORDER BY id DESC LIMIT 20").fetchall()

    lista_deptos = conn.execute("SELECT * FROM departamentos_lista ORDER BY nome ASC").fetchall()
    lista_categorias = conn.execute("SELECT * FROM categorias_financeiras ORDER BY tipo, nome ASC").fetchall()
    lista_zonas = conn.execute("SELECT * FROM zonas_lista ORDER BY nome ASC").fetchall()

    categorias_json = json.dumps([{'tipo': c['tipo'], 'nome': c['nome']} for c in lista_categorias])
    membros_json = json.dumps([dict(m) for m in todos_membros])

    conn.close()

    return render_template('dashboard.html',
                           pode_cadastro=can_cadastro(),
                           pode_tesouraria=can_tesouraria(),
                           e_admin=is_admin(),
                           total_membros=total_membros,
                           total_casamentos=total_casamentos,
                           total_mortes=total_mortes,
                           saldo_caixa=saldo_caixa,
                           saldo_banco=saldo_banco,
                           saldo_total=saldo_total,
                           todos_membros=todos_membros,
                           todas_financas=todas_financas,
                           todos_casamentos=todos_casamentos,
                           todas_mortes=todas_mortes,
                           lista_deptos=lista_deptos,
                           lista_categorias=lista_categorias,
                           lista_zonas=lista_zonas,
                           lista_usuarios=lista_usuarios,
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
                           saidas_valores=json.dumps(saidas_valores),
                           depto_labels=json.dumps(depto_labels),
                           depto_valores=json.dumps(depto_valores))

@app.route('/membros/novo', methods=['POST'])
def novo_membro():
    if not can_cadastro(): return redirect(url_for('dashboard'))
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

    conn = get_db()
    conn.execute('''
        INSERT INTO membros (
            nome, telefone, genero, data_nascimento, faixa_etaria,
            naturalidade, bairro, filiacao, tipo_documento, numero_documento,
            ano_conversao, data_batismo, posicao_atual, progressoes,
            departamento, foto_path, observacoes, data_registo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request.form['nome'].strip(),
        request.form.get('telefone', '').strip(),
        request.form.get('genero', 'Masculino'),
        request.form.get('data_nascimento', ''),
        request.form.get('faixa_etaria', 'Adulto'),
        request.form.get('naturalidade', '').strip(),
        request.form.get('bairro', ''),
        request.form.get('filiacao', '').strip(),
        request.form.get('tipo_documento', 'BI'),
        request.form.get('numero_documento', '').strip(),
        ano_conv_val,
        request.form.get('data_batismo', ''),
        request.form.get('posicao_atual', 'Membro em Comunhão'),
        request.form.get('progressoes', '').strip(),
        request.form.get('departamento', 'Geral'),
        foto_path,
        request.form.get('observacoes', '').strip(),
        datetime.now().strftime("%d/%m/%Y")
    ))
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

@app.route('/usuarios/novo', methods=['POST'])
def novo_usuario():
    if not is_admin(): return redirect(url_for('dashboard'))
    user, senha, cargo = request.form['usuario'].strip(), request.form['senha'].strip(), request.form['cargo'].strip()
    if user and senha:
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (user, senha, cargo))
            conn.commit()
        except sqlite3.IntegrityError: pass
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/usuarios/apagar/<int:id>')
def apagar_usuario(id):
    if not is_admin(): return redirect(url_for('dashboard'))
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id = ? AND id != 1", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/apagar/<tabela>/<int:id>')
def apagar_registo(tabela, id):
    if not is_admin(): return redirect(url_for('dashboard'))
    mapa = {'membro': ('membros', 'id'), 'financeiro': ('financeiro', 'id'), 'casamento': ('casamentos', 'id'), 'morte': ('mortes', 'id')}
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
        except sqlite3.IntegrityError: pass
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
        except sqlite3.IntegrityError: pass
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
