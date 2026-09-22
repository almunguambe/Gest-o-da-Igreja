from modulo_escola_biblica import CURRICULO_CLASSES, gerar_pdf_conclusao_discipulado
import os
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

import os
try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

import urllib.request
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

import os
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL and psycopg2:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn

app.secret_key = "iead_chicuque_chave_super_segura_2026"
import os
DATA_DIR = "/var/data" if os.path.exists("/var/data") else "."
DB_NAME = os.path.join(DATA_DIR, "gestao_chicuque.db")
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn



GIST_URL = "https://gist.githubusercontent.com/almunguambe/b9f7af1814fb7674e3a0dbeded9389b7/raw/33e08b96f9f953b0b9d7f277f6c6f2548d037db8/usuarios.json"

def sync_puxar_nuvem():
    """Restaura automaticamente todos os utilizadores e alunos do Gist para o SQLite local"""
    import urllib.request
    import json
    import ssl
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            GIST_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=25) as response:
            usuarios = json.loads(response.read().decode("utf-8"))
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            for u in usuarios:
                c.execute("INSERT OR REPLACE INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                          (u["usuario"], u["senha"], u["cargo"]))
            conn.commit()
            conn.close()
            print(f"✓ {len(usuarios)} utilizadores sincronizados com sucesso do Gist!")
    except Exception as e:
        print(f"Aviso sync Gist: {e}")

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

    # Contas fixas e permanentes garantidas
    contas = [
        ('admin', 'chicuque123', 'Pastor Presidente'),
        ('secretaria', '12345', 'Secretário'),
        ('tesouraria', 'senha12345', 'Tesoureiro'),
        ('doutrina', 'senha12345', 'Aluno')
    ]
    for usr, pwd, crg in contas:
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


def extrair_dados_membro(membro):
    """Extrai os dados de forma infalível usando o esquema real da base de dados."""
    def obter(chave, idx_padrao=None):
        if hasattr(membro, 'keys') and chave in membro.keys():
            return membro[chave]
        elif isinstance(membro, dict) and chave in membro:
            return membro[chave]
        elif idx_padrao is not None and not isinstance(membro, dict):
            try:
                return membro[idx_padrao]
            except:
                return None
        return None

    # Mapeamento estrito com base no PRAGMA table_info(membros)
    m_id = obter('id', 0) or 1
    nome = obter('nome', 1) or "Membro"
    telefone = str(obter('telefone', 2) or "").strip()
    faixa_etaria = obter('faixa_etaria', 5) or "Adulto"
    bairro = obter('bairro', 7) or "Chicuque Sede"
    tipo_doc = obter('tipo_documento', 9) or "BI"
    num_doc = obter('numero_documento', 10) or "---"
    ano_conv = obter('ano_conversao', 11) or "---"
    data_bat = obter('data_batismo', 12)
    posicao = obter('posicao_atual', 13) or "Membro em Comunhão"
    departamento = obter('departamento', 15) or "Geral"
    foto_path = obter('foto_path', 16) or ""

    # Formatar telefone moçambicano (+258 8x xxx xxxx)
    tel_limpo = "".join([c for c in telefone if c.isdigit()])
    if len(tel_limpo) == 9 and tel_limpo.startswith('8'):
        tel_fmt = f"(+258) {tel_limpo[:2]} {tel_limpo[2:5]} {tel_limpo[5:]}"
    elif len(tel_limpo) == 12 and tel_limpo.startswith('258'):
        tel_fmt = f"(+258) {tel_limpo[3:5]} {tel_limpo[5:8]} {tel_limpo[8:]}"
    else:
        tel_fmt = telefone if telefone else "Sem contacto"

    # Formatar data de batismo se válida
    data_bat_str = str(data_bat).strip() if data_bat else ""
    if data_bat_str.lower() in ['none', 'null', 'adulto', '']:
        data_bat_final = None
    else:
        partes = data_bat_str.split("-")
        if len(partes) == 3:
            data_bat_final = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            data_bat_final = data_bat_str

    return {
        "id": int(m_id) if str(m_id).isdigit() else 1,
        "nome": str(nome).strip(),
        "telefone": tel_fmt,
        "faixa_etaria": faixa_etaria,
        "bairro": str(bairro).strip(),
        "tipo_doc": str(tipo_doc).strip(),
        "num_doc": str(num_doc).strip(),
        "ano_conv": str(ano_conv).strip(),
        "data_batismo": data_bat_final,
        "posicao": str(posicao).strip(),
        "departamento": str(departamento).strip(),
        "foto_path": str(foto_path).strip()
    }


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


def assegurar_coluna_obito():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        if DATABASE_URL and psycopg2:
            c.execute("""
                CREATE TABLE IF NOT EXISTS obitos (
                    id SERIAL PRIMARY KEY,
                    membro_id INTEGER REFERENCES membros(id),
                    nome VARCHAR(150),
                    data_morte DATE,
                    causa TEXT,
                    observacoes TEXT,
                    data_registo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            c.execute("""
                DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE obitos ADD COLUMN membro_id INTEGER;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'membro_id ja existe';
                    END;
                END $$;
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS obitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membro_id INTEGER,
                    nome TEXT,
                    data_morte DATE,
                    causa TEXT,
                    observacoes TEXT,
                    data_registo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            try:
                c.execute("ALTER TABLE obitos ADD COLUMN membro_id INTEGER")
            except Exception:
                pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso tabela obitos: {e}")

try:
    assegurar_coluna_obito()
except Exception:
    pass


def assegurar_colunas_geograficas():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        colunas = [
            ("zona", "VARCHAR(100)"),
            ("celula", "VARCHAR(100)"),
            ("bairro", "VARCHAR(100)"),
            ("distrito", "VARCHAR(100)")
        ]
        for col, tipo in colunas:
            if DATABASE_URL and psycopg2:
                c.execute(f"""
                    DO $$ 
                    BEGIN 
                        BEGIN
                            ALTER TABLE membros ADD COLUMN {col} {tipo};
                        EXCEPTION
                            WHEN duplicate_column THEN NULL;
                        END;
                    END $$;
                """)
            else:
                try:
                    c.execute(f"ALTER TABLE membros ADD COLUMN {col} TEXT;")
                except Exception:
                    pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso migracao geografica: {e}")

try:
    assegurar_colunas_geograficas()
except Exception:
    pass

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


    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)

    
        # Carregar dúvidas bíblicas para o painel pastoral
    # Carregar dúvidas bíblicas para o painel pastoral
    duvidas_lista = []
    candidatos_discipulado = []
    try:
        c.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
        duvidas_lista = c.fetchall()
    except Exception:
        pass

    try:
        query_prog = """
            SELECT m.id, m.nome, m.foto_path, m.telefone,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
            FROM membros m
            LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
            GROUP BY m.id, m.nome, m.foto_path, m.telefone
            ORDER BY m.id DESC
        """
        c.execute(query_prog)
        candidatos_discipulado = c.fetchall()
    except Exception:
        pass

    conn.close()

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)
    return render_template('dashboard.html',
                           duvidas=duvidas_lista,
                           discipulado_alunos=candidatos_discipulado,
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
def estudos():
    from flask import redirect
    return redirect('/discipulado/classe/c1')

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
    zona = request.form.get('zona', '').strip()
    celula = request.form.get('celula', '').strip()
    distrito = request.form.get('distrito', '').strip()
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

    # Inserção do Logo Oficial no Cartão
    logo_path = obter_caminho_logo()
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 0.4*cm, 4.3*cm, width=0.9*cm, height=0.9*cm, preserveAspectRatio=True, mask='auto')
        except Exception as err:
            print(f"Aviso logo cartao: {err}")

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

    elementos.append(Paragraph(f"<para ><font color='#1e293b' size=13>{corpo}</font>", ParagraphStyle('B', alignment=4, spaceAfter=25)))
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
    zona = request.form.get('zona', '').strip()
    celula = request.form.get('celula', '').strip()
    distrito = request.form.get('distrito', '').strip()
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
    zona = request.form.get('zona', '').strip()
    celula = request.form.get('celula', '').strip()
    distrito = request.form.get('distrito', '').strip()
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


# ==============================================================================
# MANUAL DE DOUTRINA DE 6 MESES (24 LIÇÕES DETALHADAS)
# ==============================================================================
MODULOS_DOUTRINA_SEMESTRAL = [
    {
        "modulo": 1,
        "titulo": "Mês 1 – Fundamentos da Fé, Queda e Redenção",
        "licoes": [
            {"semana": 1, "tema": "A Criação de Deus e a Queda do Homem", "texto": "Gênesis 1 a 3. Compreensão do propósito divino, a desobediência original, a corrupção da natureza humana e a separação espiritual."},
            {"semana": 2, "tema": "O Plano Eterno da Redenção", "texto": "João 3:16; Isaías 53. A provisão vicária de Deus por meio da encarnação, vida imaculada e sacrifício expiatório de Cristo na cruz."},
            {"semana": 3, "tema": "Arrependimento e Confissão Bíblica", "texto": "Atos 3:19; 1 João 1:9. O reconhecimento sincero do pecado, a tristeza segundo Deus e a mudança radical de mente e direção moral."},
            {"semana": 4, "tema": "Justificação e Regeneração (O Novo Nascimento)", "texto": "Romanos 5:1; Tito 3:5. A reconciliação legal perante a justiça divina e a nova vida gerada pelo Espírito Santo."}
        ]
    },
    {
        "modulo": 2,
        "titulo": "Mês 2 – As Sagradas Escrituras e a Trindade Divina",
        "licoes": [
            {"semana": 5, "tema": "A Bíblia Sagrada: Inspiração e Inerrância", "texto": "2 Timóteo 3:16-17; 2 Pedro 1:20-21. Como a Palavra de Deus foi inspirada, a sua autoridade suprema e a regra inegociável de fé e conduta."},
            {"semana": 6, "tema": "Deus Pai: Soberania, Santidade e Amor", "texto": "Salmo 139; 1 João 4:8. A transcendência de Deus, Sua criação, sustento de todas as coisas e paternidade para com os salvos."},
            {"semana": 7, "tema": "Deus Filho: Divindade, Humanidade e Ministério", "texto": "João 1:1-14; Filipenses 2:5-11. A divindade eterna de Jesus Cristo, Sua ressurreição corpórea e intercessão à destra do Pai."},
            {"semana": 8, "tema": "Deus Espírito Santo: Pessoa, Papel e Convencimento", "texto": "João 16:7-14. O Consolador como terceira Pessoa da Trindade, que regenera, habita, guia e instrui o crente."}
        ]
    },
    {
        "modulo": 3,
        "titulo": "Mês 3 – As Ordenanças da Igreja e a Vida em Comunhão",
        "licoes": [
            {"semana": 9, "tema": "O Batismo nas Águas por Imersão", "texto": "Mateus 28:19; Romanos 6:3-4. O mandamento de Jesus: simbolismo da sepultura do velho homem e ressurreição para uma vida em novidade."},
            {"semana": 10, "tema": "Requisitos Bíblicos para o Batismo", "texto": "Marcos 16:16; Atos 8:36-38. Fé genuína, frutos visíveis de arrependimento e a declaração pública de lealdade a Cristo."},
            {"semana": 11, "tema": "A Santa Ceia do Senhor: Memória e Proclamação", "texto": "1 Coríntios 11:23-30. O pão e o fruto da vide como corpo e sangue de Cristo; autoexame, discernimento e comunhão santa."},
            {"semana": 12, "tema": "A Igreja como Corpo de Cristo e Família de Deus", "texto": "1 Coríntios 12:12-27; Efésios 4:1-6. Membros uns dos outros, submissão mútua, discipulado e compromisso na congregação local."}
        ]
    },
    {
        "modulo": 4,
        "titulo": "Mês 4 – Santificação, Oração e Mordomia Cristã",
        "licoes": [
            {"semana": 13, "tema": "Santificação Diária e Separação do Mundo", "texto": "1 Tessalonicenses 4:3-7; Hebreus 12:14. O processo contínuo de consagração e vitória sobre as concupiscências carnais."},
            {"semana": 14, "tema": "A Vida Devocional: Oração Eficaz e Jejum", "texto": "Mateus 6:5-18; Tiago 5:16. Prática sistemática de oração, adoração particular e busca de intimidade com Deus."},
            {"semana": 15, "tema": "Mordomia Financeira: Dízimos e Ofertas", "texto": "Malaquias 3:10; 2 Coríntios 9:6-8. Fidelidade nos dízimos como princípio de gratidão e sustentação da obra missionária e eclesial."},
            {"semana": 16, "tema": "A Conduta do Cristão na Família e na Sociedade", "texto": "Efésios 5:21-6:4; Mateus 5:13-16. Sal da terra e luz do mundo, pureza moral, casamentos santos e honra no trabalho."}
        ]
    },
    {
        "modulo": 5,
        "titulo": "Mês 5 – Doutrina Pentecostal e Poder do Espírito Santo",
        "licoes": [
            {"semana": 17, "tema": "A Promessa do Batismo no Espírito Santo", "texto": "Joel 2:28-29; Atos 1:8. Revestimento de poder concedido aos salvos para testemunhar o Evangelho com intrepidez."},
            {"semana": 18, "tema": "A Evidência Bíblica e as Línguas Estranhas", "texto": "Atos 2:1-4; 10:44-46. O dom de falar noutras línguas como confirmação bíblica inicial do batismo pentecostal."},
            {"semana": 19, "tema": "Os Dons Espirituais e a Edificação Coletiva", "texto": "1 Coríntios 12 e 14. Dons de revelação, poder e elocução: operação ordenada e orientada pelo amor cristão."},
            {"semana": 20, "tema": "Batalha Espiritual e a Armadura Completa de Deus", "texto": "Efésios 6:10-18. Resistência firme contra as ciladas das trevas, vigilância e triunfo em nome de Jesus."}
        ]
    },
    {
        "modulo": 6,
        "titulo": "Mês 6 – Grande Comissão, Ordem Eclesial e Esperança Bendita",
        "licoes": [
            {"semana": 21, "tema": "A Grande Comissão e Evangelismo Pessoal", "texto": "Marcos 16:15; Atos 4:20. O dever intransferível de cada crente de partilhar a mensagem do Evangelho no seu círculo social."},
            {"semana": 22, "tema": "Estrutura e Disciplina Eclesiástica da IEAD", "texto": "Hebreus 13:17; 1 Timóteo 3. Respeito à liderança pastoral, presbitério, diáconos e normas de convivência assembleiana."},
            {"semana": 23, "tema": "Escatologia Bíblica: O Arrebatamento e a Segunda Vinda", "texto": "1 Tessalonicenses 4:13-18; Tito 2:13. A bendita esperança da Igreja, julgamento vindouro e eternidade com Cristo."},
            {"semana": 24, "tema": "Exame Final de Fé e Preparação Prática para o Batismo", "texto": "Confissão pública dos artigos de fé, orientações práticas de vestimenta e consagração solene para as águas."}
        ]
    }
]

# ==============================================================================
# ROTAS PARA CERTIFICADO DE BATISMO, CARTA DE RECOMENDAÇÃO E CARTÃO
# ==============================================================================
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def obter_caminho_logo():
    caminho = os.path.join(app.root_path, "static", "logo.png")
    if os.path.exists(caminho):
        return caminho
    caminho_rel = os.path.join("static", "logo.png")
    if os.path.exists(caminho_rel):
        return os.path.abspath(caminho_rel)
    return None

@app.route('/membro/<int:id>/certificado_batismo')
@app.route('/membro/certificado_pdf/<int:id>/batismo')
def emitir_certificado_batismo(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado.", 404

        dados = extrair_dados_membro(membro)

        if not dados['data_batismo']:
            return """
            <div style="font-family: 'Segoe UI', Arial, sans-serif; text-align: center; margin-top: 60px; color: #333;">
                <div style="background: #fff; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #d9534f;">
                    <h3 style="color: #c9302c; margin-bottom: 10px;">Data de Batismo Necessária</h3>
                    <p style="color: #666; font-size: 15px; line-height: 1.5;">O membro selecionado ainda não tem a <b>Data de Batismo</b> registada na ficha.</p>
                    <p style="color: #888; font-size: 13px;">Preencha a data do batismo no formulário antes de gerar o documento solene.</p>
                    <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 24px; background-color: #0d3b66; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">Voltar ao Painel</a>
                </div>
            </div>
            """, 400

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=2.5*cm,
            rightMargin=2.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        elementos = []
        estilos = getSampleStyleSheet()

        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=70, height=70))
                elementos.append(Spacer(1, 4))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=2)
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#666666'), spaceAfter=10)
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=24, alignment=1, textColor=colors.HexColor('#b38600'), spaceAfter=14)
        estilo_intro = ParagraphStyle('Intro', parent=estilos['Normal'], fontName='Helvetica', fontSize=12, leading=18, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=22, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=8)
        estilo_detalhes = ParagraphStyle('Detalhes', parent=estilos['Normal'], fontName='Helvetica', fontSize=12, leading=18, alignment=1, textColor=colors.HexColor('#333333'))
        estilo_versiculo = ParagraphStyle('Verso', parent=estilos['Normal'], fontName='Helvetica-Oblique', fontSize=9.5, leading=14, alignment=1, textColor=colors.HexColor('#777777'))

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph(f"CONGREGAÇÃO DE {dados['bairro'].upper()} – MOÇAMBIQUE", estilo_sub))
        elementos.append(Paragraph("CERTIFICADO DE BATISMO NAS ÁGUAS", estilo_tit))

        elementos.append(Paragraph("Certificamos para os devidos fins eclesiásticos que o(a) nosso(a) irmão(ã)", estilo_intro))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(f"<b>{dados['nome'].upper()}</b>", estilo_nome))

        texto_declaracao = f"tendo confessado publicamente a Jesus Cristo como seu Salvador pessoal, desceu às águas batismais por imersão em <b>{dados['data_batismo']}</b>, cumprindo a sagrada ordenança em nome do Pai, do Filho e do Espírito Santo."
        elementos.append(Paragraph(texto_declaracao, estilo_detalhes))
        elementos.append(Spacer(1, 10))

        versiculo = '&quot;Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo; ensinando-os a guardar todas as coisas que eu vos tenho mandado.&quot; — <b>Mateus 28:19-20</b>'
        elementos.append(Paragraph(versiculo, estilo_versiculo))
        elementos.append(Spacer(1, 28))

        tabela_ass = Table([
            ["__________________________________________", "__________________________________________"],
            ["Pastor Presidente / Titular", "Secretaria Geral da Igreja"]
        ], colWidths=[12.5*cm, 12.5*cm])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#444444')),
            ('TOPPADDING', (0,0), (-1,-1), 4)
        ]))
        elementos.append(tabela_ass)

        def desenhar_moldura(canvas, doc):
            canvas.saveState()
            largura, altura = landscape(A4)
            canvas.setStrokeColor(colors.HexColor('#0d3b66'))
            canvas.setLineWidth(4)
            canvas.rect(1.2*cm, 1.2*cm, largura - 2.4*cm, altura - 2.4*cm)
            canvas.setStrokeColor(colors.HexColor('#d4af37'))
            canvas.setLineWidth(1.5)
            canvas.rect(1.5*cm, 1.5*cm, largura - 3.0*cm, altura - 3.0*cm)
            canto = 0.6*cm
            canvas.setFillColor(colors.HexColor('#0d3b66'))
            canvas.rect(1.5*cm, altura - 1.5*cm - canto, canto, canto, fill=1, stroke=0)
            canvas.rect(largura - 1.5*cm - canto, altura - 1.5*cm - canto, canto, canto, fill=1, stroke=0)
            canvas.rect(1.5*cm, 1.5*cm, canto, canto, fill=1, stroke=0)
            canvas.rect(largura - 1.5*cm - canto, 1.5*cm, canto, canto, fill=1, stroke=0)
            canvas.restoreState()

        doc.build(elementos, onFirstPage=desenhar_moldura)
        buffer.seek(0)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Certificado_Batismo_{id}.pdf")
    except Exception as e:
        return f"Erro ao processar certificado: {e}", 500
@app.route('/membro/<int:id>/carta_recomendacao')
@app.route('/membro/certificado_pdf/<int:id>/recomendacao')
def emitir_carta_recomendacao(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado.", 404

        dados = extrair_dados_membro(membro)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        elementos = []
        estilos = getSampleStyleSheet()

        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=65, height=65))
                elementos.append(Spacer(1, 8))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'))
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, textColor=colors.HexColor('#222222'))
        estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, leading=19, alignment=4)

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph(f"CONGREGAÇÃO DE {dados['bairro'].upper()} – MOÇAMBIQUE", estilo_sub))
        elementos.append(Spacer(1, 20))
        elementos.append(Paragraph("CARTA PASTORAL DE RECOMENDAÇÃO", estilo_tit))
        elementos.append(Spacer(1, 25))

        nome_l = dados['nome'].replace("<", "").replace(">", "")
        cargo_l = dados['posicao'].replace("<", "").replace(">", "")
        cong_l = dados['bairro'].replace("<", "").replace(">", "")
        depto_l = dados['departamento'].replace("<", "").replace(">", "")

        elementos.append(Paragraph("Aos Amados Irmãos em Cristo da Igreja Co-Irmã:", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Pela presente, temos a honra de recomendar à vossa comunhão e aos santos cuidados o(a) estimado(a) irmão(ã) <b>{nome_l}</b>, que serve nesta comunidade eclesial na qualidade de <b>{cargo_l}</b> (Ministério/Departamento: <b>{depto_l}</b>).", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Enquanto esteve connosco na congregação de <b>{cong_l}</b>, manteve um testemunho exemplar, irrepreensível e fiel aos princípios das Sagradas Escrituras e aos estatutos eclesiásticos da nossa denominação.", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("Rogamos que o(a) recebam no Senhor com todo o apreço e hospitalidade cristã, prestando-lhe todo o apoio e acompanhamento espiritual na continuação da sua jornada de fé.", estilo_corpo))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>&quot;Portanto, recebei-vos uns aos outros, como também Cristo nos recebeu para glória de Deus.&quot; (Romanos 15:7)</i>", estilo_corpo))
        elementos.append(Spacer(1, 35))
        elementos.append(Paragraph(f"{cong_l}, Moçambique.", estilo_corpo))
        elementos.append(Spacer(1, 35))

        tabela_ass = Table([
            ["__________________________________________", "__________________________________________"],
            ["Pastor Presidente / Titular", "Secretaria da Igreja"]
        ], colWidths=[8.5*cm, 8.5*cm])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9)
        ]))
        elementos.append(tabela_ass)

        doc.build(elementos)
        buffer.seek(0)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Carta_Recomendacao_{id}.pdf")
    except Exception as e:
        return f"Erro ao processar carta: {e}", 500

@app.route('/membro/certificado_pdf/<int:id>/apresentacao')
def emitir_certificado_apresentacao(id):
    return emitir_certificado_batismo(id)


# ==============================================================================
# DISCIPULADO BÍBLICO PROGRESSIVO & CERTIFICADO DE CONCLUSÃO
# ==============================================================================

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


@app.route('/discipulado/responder_duvida/<int:id>', methods=['POST'])
def responder_duvida_discipulado(id):
    from flask import request, redirect
    resposta = request.form.get('resposta', '').strip()
    if resposta:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                UPDATE duvidas_discipulado 
                SET resposta = %s 
                WHERE id = %s
            """ if DATABASE_URL and psycopg2 else """
                UPDATE duvidas_discipulado 
                SET resposta = ? 
                WHERE id = ?
            """, (resposta, id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao salvar resposta: {e}")
    return redirect('/#secao-discipulado')

@app.route('/manifest.json')
def serve_manifest():
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
def serve_sw():
    from flask import send_from_directory
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')