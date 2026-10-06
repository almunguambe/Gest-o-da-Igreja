import qrcode
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
from flask import flash, Flask, render_template, request, redirect, url_for, session, send_file
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# ReportLab para PDFs
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
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

class CompatCursor:
    def __init__(self, cursor, is_pg=False):
        self._cur = cursor
        self._is_pg = is_pg
    def execute(self, sql, params=None):
        if self._is_pg and sql:
            # Converte ? para %s para PostgreSQL
            sql = sql.replace('?', '%s')
        if params is not None:
            return self._cur.execute(sql, params)
        return self._cur.execute(sql)
    def fetchone(self):
        return self._cur.fetchone()
    def fetchall(self):
        return self._cur.fetchall()
    def fetchmany(self, size=None):
        return self._cur.fetchmany(size)
    @property
    def lastrowid(self):
        return getattr(self._cur, 'lastrowid', None)
    def __iter__(self):
        return iter(self._cur)

class CompatConn:
    def __init__(self, conn, is_pg=False):
        self._conn = conn
        self._is_pg = is_pg
    def cursor(self):
        return CompatCursor(self._conn.cursor(), self._is_pg)
    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur
    def commit(self):
        return self._conn.commit()
    def rollback(self):
        return self._conn.rollback()
    def close(self):
        return self._conn.close()

def get_db():
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url and psycopg2:
        try:
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return CompatConn(conn, is_pg=True)
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL, usando fallback SQLite: {e}")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return CompatConn(conn, is_pg=False)

def executar_migracao_garantida():
    try:
        conn = get_db()
        c = conn.cursor()
        
        # 1. Tabela igrejas
        c.execute("""
            CREATE TABLE IF NOT EXISTS igrejas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                cidade TEXT,
                distrito TEXT,
                pastor TEXT,
                telefone TEXT,
                ativa INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("SELECT id FROM igrejas WHERE id = 1")
        if not c.fetchone():
            c.execute("""
                INSERT INTO igrejas (id, nome, cidade, distrito, pastor, telefone, ativa)
                VALUES (1, 'Congregação de Chicuque', 'Maxixe', 'Maxixe', 'Pastor Local', '+258 84 000 0000', 1)
            """)
        
        # 2. Adicionar igreja_id nas tabelas
        tabelas = [
            'usuarios', 'membros', 'financeiro', 'transferencias', 
            'casamentos', 'mortes', 'cultos_frequencia', 'novos_convertidos', 
            'patrimonio', 'escalas', 'campanhas_metas', 'zonas_lista', 
            'departamentos_lista', 'categorias_financeiras'
        ]
        for t in tabelas:
            try:
                c.execute(f"PRAGMA table_info({t})")
                colunas = [col[1] for col in c.fetchall()]
                if colunas and 'igreja_id' not in colunas:
                    c.execute(f"ALTER TABLE {t} ADD COLUMN igreja_id INTEGER DEFAULT 1")
            except Exception:
                pass
                
        # 3. Coluna is_superadmin em usuarios
        try:
            c.execute("PRAGMA table_info(usuarios)")
            cols_u = [col[1] for col in c.fetchall()]
            if 'is_superadmin' not in cols_u:
                c.execute("ALTER TABLE usuarios ADD COLUMN is_superadmin INTEGER DEFAULT 0")
            c.execute("UPDATE usuarios SET is_superadmin = 1, igreja_id = 1 WHERE usuario = 'admin'")
        except Exception:
            pass

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso migracao inicial: {e}")

executar_migracao_garantida()




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
    c.execute('''CREATE TABLE IF NOT EXISTS igrejas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        cidade TEXT,
        distrito TEXT,
        pastor TEXT,
        telefone TEXT,
        ativa INTEGER DEFAULT 1,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("SELECT id FROM igrejas WHERE id = 1")
    if not c.fetchone():
        c.execute("INSERT INTO igrejas (id, nome, cidade, distrito, pastor, telefone, ativa) VALUES (1, 'Congregação de Chicuque', 'Maxixe', 'Maxixe', 'Pastor Local', '+258 84 000 0000', 1)")
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL
    )''')
    
    try:
        c.execute("ALTER TABLE membros ADD COLUMN estado_civil TEXT DEFAULT 'Solteiro(a)'")
    except: pass

    
    # Novas tabelas de configuração eclesiástica
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS config_cargos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_cultos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_contas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config_atividades (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS igrejas_distritos (id INTEGER PRIMARY KEY AUTOINCREMENT, provincia TEXT, distrito TEXT, nome TEXT)''')
    except:
        pass

    
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS config_eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    except: pass

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
            
            # Contexto Multi-Igreja
            igreja_id = user['igreja_id'] if ('igreja_id' in user.keys() and user['igreja_id']) else 1
            session['igreja_id'] = igreja_id
            session['is_superadmin'] = bool(user['is_superadmin']) if 'is_superadmin' in user.keys() else False

            conn_ig = get_db()
            ig_info = conn_ig.execute('SELECT nome FROM igrejas WHERE id = ?', (igreja_id,)).fetchone()
            conn_ig.close()
            session['igreja_nome'] = ig_info['nome'] if ig_info else 'IEAD - Congregação Local'

            if user['cargo'] == 'Estudante':
                return redirect('/estudos')
            return redirect('/')
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
        return redirect('/estudos')

    conn = get_db()
    
    # Contexto Multi-Igreja
    is_super = session.get('is_superadmin', False)
    req_igreja = request.args.get('igreja_id', type=int)
    if is_super and req_igreja:
        igreja_id = req_igreja
        session['igreja_id'] = igreja_id
        ig_row = conn.execute("SELECT nome FROM igrejas WHERE id = ?", (igreja_id,)).fetchone()
        if ig_row:
            session['igreja_nome'] = ig_row['nome']
    else:
        igreja_id = session.get('igreja_id', 1)

    lista_igrejas = conn.execute("SELECT * FROM igrejas WHERE ativa = 1 ORDER BY nome ASC").fetchall() if is_super else []

    total_membros = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]
    total_casamentos = conn.execute("SELECT COUNT(*) FROM casamentos WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]
    total_mortes = conn.execute("SELECT COUNT(*) FROM mortes WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]

    entrada_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Entrada' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)", (igreja_id,)).fetchone()[0] or 0.0
    saida_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Saída' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)", (igreja_id,)).fetchone()[0] or 0.0
    saldo_caixa = entrada_caixa - saida_caixa

    entrada_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Entrada' AND local_movimento = 'Banco'", (igreja_id,)).fetchone()[0] or 0.0
    saida_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Saída' AND local_movimento = 'Banco'", (igreja_id,)).fetchone()[0] or 0.0
    saldo_banco = entrada_banco - saida_banco
    saldo_total = (entrada_caixa + entrada_banco) - (saida_caixa + saida_banco)

    hoje_md = datetime.now().strftime("-%m-%d")
    aniversariantes_dia = conn.execute("SELECT nome, data_nascimento, telefone, departamento FROM membros WHERE igreja_id = ? AND data_nascimento LIKE ?", (igreja_id, f"%{hoje_md}")).fetchall()

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

    todos_membros = conn.execute("SELECT * FROM membros WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todas_financas = conn.execute("SELECT * FROM financeiro WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todos_casamentos = conn.execute("SELECT * FROM casamentos WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todas_mortes = conn.execute("SELECT * FROM mortes WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todos_cultos = conn.execute("SELECT * FROM cultos_frequencia WHERE igreja_id = ? ORDER BY id DESC LIMIT 25", (igreja_id,)).fetchall()
    todos_convertidos = conn.execute("SELECT * FROM novos_convertidos WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todo_patrimonio = conn.execute("SELECT * FROM patrimonio WHERE igreja_id = ? ORDER BY departamento, item ASC", (igreja_id,)).fetchall()
    conn.execute("""CREATE TABLE IF NOT EXISTS escalas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_escala TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        dirigente TEXT,
        pregador TEXT,
        leitura_palavra TEXT,
        louvor_grupo TEXT,
        diaconos_servico TEXT,
        observacoes TEXT,
        telefone_dirigente TEXT,
        telefone_pregador TEXT,
        igreja_id INTEGER DEFAULT 1
    )""")
        # Garantir estrutura completa da tabela escalas
    conn.execute('''CREATE TABLE IF NOT EXISTS escalas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_escala TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        dirigente TEXT,
        pregador TEXT,
        leitura_palavra TEXT,
        louvor_grupo TEXT,
        diaconos_servico TEXT,
        observacoes TEXT,
        telefone_dirigente TEXT,
        telefone_pregador TEXT,
        igreja_id INTEGER DEFAULT 1
    )''')
    for col in ['telefone_dirigente', 'telefone_pregador', 'igreja_id']:
        try:
            conn.execute(f"ALTER TABLE escalas ADD COLUMN {col} TEXT")
            conn.commit()
        except Exception:
            pass
    todas_escalas = conn.execute("SELECT * FROM escalas WHERE igreja_id = ? ORDER BY data_escala DESC LIMIT 20", (igreja_id,)).fetchall()
    lista_usuarios = conn.execute("SELECT id, usuario, cargo FROM usuarios WHERE igreja_id = ? ORDER BY id ASC", (igreja_id,)).fetchall()
    ultimas_transferencias = conn.execute("SELECT * FROM transferencias WHERE igreja_id = ? ORDER BY id DESC LIMIT 20", (igreja_id,)).fetchall()
    lista_avaliacoes = conn.execute("SELECT * FROM avaliacoes_estudantes ORDER BY id DESC").fetchall()
    todas_duvidas = conn.execute("SELECT * FROM duvidas_estudantes ORDER BY id DESC").fetchall()

    lista_deptos = conn.execute("SELECT * FROM departamentos_lista ORDER BY nome ASC").fetchall()
    lista_categorias = conn.execute("SELECT * FROM categorias_financeiras ORDER BY tipo, nome ASC").fetchall()
    try:
        lista_zonas = conn.execute("SELECT * FROM zonas_lista ORDER BY nome ASC").fetchall()
    except Exception:
        lista_zonas = []

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
        # Buscar lista de Professores/Mentores disponiveis
        professores_discipulado = []
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '')
            # Membros com ministerio ou em comunhao aptos para discipular
            if any(term in f_val.lower() for term in ['pastor', 'presb', 'diacon', 'evang', 'obreir', 'lider', 'comunh']):
                professores_discipulado.append(m)
        if not professores_discipulado:
            professores_discipulado = todos_membros

        # Query de progresso trazendo professor_nome
        query_prog = """
            SELECT m.id, m.nome, m.foto_path, m.telefone,
                   COALESCE(m.professor_nome, 'A designar') as prof_nome,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
            FROM membros m
            LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
            WHERE LOWER(COALESCE(m.funcao, '')) LIKE '%candidat%'
               OR LOWER(COALESCE(m.funcao, '')) LIKE '%prova%'
               OR LOWER(COALESCE(m.funcao, '')) LIKE '%convertid%'
               OR LOWER(COALESCE(m.batizado, '')) IN ('nao', 'não', 'pendente', '')
            GROUP BY m.id, m.nome, m.foto_path, m.telefone, m.professor_nome
            ORDER BY m.id DESC
        """
        try:
            c.execute(query_prog)
            candidatos_discipulado = c.fetchall()
        except Exception:
            # Fallback caso a coluna ainda esteja a sincronizar
            query_prog_fb = """
                SELECT m.id, m.nome, m.foto_path, m.telefone,
                       'A designar' as prof_nome,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
                FROM membros m
                LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
                GROUP BY m.id, m.nome, m.foto_path, m.telefone
                ORDER BY m.id DESC
            """
            c.execute(query_prog_fb)
            candidatos_discipulado = c.fetchall()
    except Exception:
        pass

    conn.close()

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)
    
    try:
        planos = conn.execute("SELECT * FROM actividades_planeamento ORDER BY id DESC").fetchall()
    except Exception:
        planos = []
    # Filtrar Candidatos ao Batismo diretamente da lista oficial de membros em memoria
    candidatos_batismo = []
    for m in todos_membros:
        # Suporta dicionario (PostgreSQL/RealDictCursor) e sqlite3.Row
        f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
        b_val = str(m.get('batizado', '') if hasattr(m, 'get') else m['batizado'] if 'batizado' in m.keys() else '').lower()
        
        # Considera candidatos ao batismo, membros em prova ou nao batizados
        if ('candidat' in f_val) or ('prova' in f_val) or ('convertid' in f_val) or (b_val in ['nao', 'não', 'pendente', '']):
            candidatos_batismo.append(m)

    # Se a lista filtrada estiver vazia, disponibiliza todos os membros para permitir selecao imediata
    if not candidatos_batismo:
        candidatos_batismo = todos_membros

    return render_template('dashboard.html', professores_discipulado=professores_discipulado, candidatos_batismo=candidatos_batismo, planos=planos,
                           todos_membros=todos_membros,
                           lista_igrejas=lista_igrejas if 'lista_igrejas' in locals() else [],
                           lista_zonas=lista_zonas if 'lista_zonas' in locals() else [],
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
                           saidas_valores=json.dumps(saidas_valores)
    )


@app.route('/portal_estudos')
def portal_estudos():
    return redirect('/estudos')

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
    
    return redirect('/estudos')

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
    return redirect('/estudos')

@app.route('/membros/novo', methods=['POST'])
def novo_membro():
    if not can_cadastro(): return redirect('/')
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
            return redirect('/')

    existente_nome = conn.execute("SELECT id FROM membros WHERE LOWER(TRIM(nome)) = LOWER(?)", (nome,)).fetchone()
    if existente_nome:
        conn.close()
        session['alerta_duplicado'] = f"O membro '{nome}' já se encontra registado."
        return redirect('/')

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

    # Verificação obrigatória do campo Zona
    if not zona:
        conn.close()
        session['alerta_duplicado'] = "O campo Zona é de preenchimento obrigatório."
        return redirect('/')

    c = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    marcador = "%s" if is_pg else "?"

    sql_insert = f"""
        INSERT INTO membros (
            nome, telefone, genero, data_nascimento, faixa_etaria,
            naturalidade, bairro, zona, celula, distrito,
            filiacao, tipo_documento, numero_documento,
            ano_conversao, data_batismo, posicao_atual, progressoes,
            departamento, foto_path, observacoes, data_registo, estado
        ) VALUES ({', '.join([marcador]*22)})
    """

    valores = (
        nome, request.form.get('telefone', '').strip(), request.form.get('genero', 'Masculino'),
        request.form.get('data_nascimento', ''), request.form.get('faixa_etaria', 'Adulto'),
        request.form.get('naturalidade', '').strip(), request.form.get('bairro', '').strip(),
        zona, celula, distrito,
        request.form.get('filiacao', '').strip(), tipo_doc, num_doc, ano_conv_val,
        request.form.get('data_batismo', ''), request.form.get('posicao_atual', 'Membro em Comunhão'),
        request.form.get('progressoes', '').strip(), request.form.get('departamento', 'Geral'),
        foto_path, request.form.get('observacoes', '').strip(), datetime.now().strftime("%d/%m/%Y"),
        'Activo'
    )

    if is_pg:
        c.execute(sql_insert, valores)
    else:
        conn.execute(sql_insert, valores)

    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = f"Membro '{nome}' registado com sucesso!"
    return redirect('/')

@app.route('/cultos/novo', methods=['POST'])
def novo_culto():
    if not can_cadastro(): return redirect('/')
    h = int(request.form.get('homens') or 0)
    m = int(request.form.get('mulheres') or 0)
    jh = int(request.form.get('jovens_homens') or 0)
    jm = int(request.form.get('jovens_mulheres') or 0)
    cm = int(request.form.get('criancas_meninos') or 0)
    cf = int(request.form.get('criancas_meninas') or 0)
    vh = int(request.form.get('visitantes_homens') or 0)
    vf = int(request.form.get('visitantes_mulheres') or 0)
    nc = int(request.form.get('novos_convertidos') or 0)

    j_total = jh + jm
    c_total = cm + cf
    v_total = vh + vf
    total = h + m + j_total + c_total + v_total

    conn = get_db()
    # Auto-cura de colunas caso nao existam na tabela ativa
    for col in ['jovens_homens', 'jovens_mulheres', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres']:
        try:
            conn.execute(f"ALTER TABLE cultos_frequencia ADD COLUMN {col} INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            pass

    try:
        conn.execute('''INSERT INTO cultos_frequencia (data_culto, tipo_culto, homens, mulheres, jovens_homens, jovens_mulheres, jovens, criancas_meninos, criancas_meninas, criancas, visitantes_homens, visitantes_mulheres, visitantes, novos_convertidos, total_presentes, pregador, tema_mensagem, data_registo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['data_culto'], request.form['tipo_culto'], h, m, jh, jm, j_total, cm, cf, c_total, vh, vf, v_total, nc, total,
                      request.form.get('pregador', ''), request.form.get('tema_mensagem', ''), datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
    except Exception as e:
        # Fallback de compatibilidade
        conn.execute('''INSERT INTO cultos_frequencia (data_culto, tipo_culto, homens, mulheres, jovens, criancas, visitantes, novos_convertidos, total_presentes, pregador, tema_mensagem, data_registo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['data_culto'], request.form['tipo_culto'], h, m, j_total, c_total, v_total, nc, total,
                      request.form.get('pregador', ''), request.form.get('tema_mensagem', ''), datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
    finally:
        conn.close()

    session['sucesso_cadastro'] = "Culto e frequência registados!"
    return redirect('/')

@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    if not can_cadastro(): return redirect('/')
    conn = get_db()
    conn.execute('''INSERT INTO novos_convertidos (nome, telefone, bairro, data_decisao, culto_origem, quem_convidou, status_discipulado, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (request.form['nome'].strip(), request.form.get('telefone', '').strip(), request.form.get('bairro', ''),
                  request.form['data_decisao'], request.form.get('culto_origem', ''), request.form.get('quem_convidou', ''),
                  request.form.get('status_discipulado', 'Decisão Inicial'), request.form.get('observacoes', '')))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Novo convertido registado!"
    return redirect('/')

@app.route('/convertidos/atualizar_status/<int:id>', methods=['POST'])
def atualizar_status_convertido(id):
    if not can_cadastro(): return redirect('/')
    novo_status = request.form.get('status_discipulado')
    conn = get_db()
    conn.execute("UPDATE novos_convertidos SET status_discipulado = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/patrimonio/novo', methods=['POST'])
def novo_patrimonio():
    if not is_admin(): return redirect('/')
    conn = get_db()
    conn.execute('''INSERT INTO patrimonio (item, departamento, quantidade, estado_conservacao, localizacao, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (request.form['item'].strip(), request.form.get('departamento', 'Geral'),
                  int(request.form.get('quantidade') or 1), request.form.get('estado_conservacao', 'Bom'),
                  request.form.get('localizacao', 'Templo Sede'), request.form.get('observacoes', '')))
    conn.commit()
    conn.close()
    session['sucesso_cadastro'] = "Património registado!"
    return redirect('/')

@app.route('/escalas/novo', methods=['GET', 'POST'])
def nova_escala():
     if request.method == 'GET':
         return redirect('/#aba-escalas')
         
     if not is_admin() and not can_cadastro(): 
         return redirect('/')
         
     data_escala = request.form.get('data_escala', '').strip()
     tipo_culto = request.form.get('tipo_culto', '').strip()
     
     if not data_escala or not tipo_culto:
         flash("Por favor, preencha a data e o tipo de culto da escala.", "erro")
         return redirect('/#aba-escalas')

     conn = get_db()
     conn.execute('''CREATE TABLE IF NOT EXISTS escalas (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         data_escala TEXT NOT NULL,
         tipo_culto TEXT NOT NULL,
         dirigente TEXT,
         pregador TEXT,
         leitura_palavra TEXT,
         louvor_grupo TEXT,
         diaconos_servico TEXT,
         observacoes TEXT,
         telefone_dirigente TEXT,
         telefone_pregador TEXT,
         igreja_id INTEGER DEFAULT 1
     )''')
     
     igreja_id = session.get('igreja_id', 1)
     conn.execute('''INSERT INTO escalas (data_escala, tipo_culto, dirigente, pregador, leitura_palavra, louvor_grupo, diaconos_servico, observacoes, telefone_dirigente, telefone_pregador, igreja_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data_escala, tipo_culto, request.form.get('dirigente', ''),
                   request.form.get('pregador', ''), request.form.get('leitura_palavra', ''),
                   request.form.get('louvor_grupo', ''), request.form.get('diaconos_servico', ''), request.form.get('observacoes', ''),
                   request.form.get('telefone_dirigente', ''), request.form.get('telefone_pregador', ''), igreja_id))
     conn.commit()
     conn.close()
     flash("Escala de culto registada com sucesso!", "sucesso")
     return redirect('/#aba-escalas')

@app.route('/escalas/pdf/<int:id>')
def escala_pdf(id):
    conn = get_db()
    e = conn.execute("SELECT * FROM escalas WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not e: return redirect('/')

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

@app.route('/validar/membro/<int:id>')
def validar_membro_publico(id):
    conn = get_db()
    membro = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    cong_nome = "IEAD - Congregação Local"
    if membro and 'igreja_id' in membro.keys() and membro['igreja_id']:
        ig = conn.execute("SELECT nome FROM igrejas WHERE id = ?", (membro['igreja_id'],)).fetchone()
        if ig:
            cong_nome = ig['nome']
    conn.close()
    return render_template('validar_membro.html', membro=membro, congregacao_nome=cong_nome)

@app.route('/membro/cartao_pdf/<int:id>')
def cartao_membro_pdf(id):
    if not can_cadastro(): return redirect('/')
    conn = get_db()
    m = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not m: return redirect('/')

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

    # Geração e Inserção do QR Code de Validação Oficial SIGAD
    try:
        url_validacao = request.host_url.rstrip('/') + f"/validar/membro/{m['id']}"
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url_validacao)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        qr_buf = io.BytesIO()
        img_qr.save(qr_buf, format='PNG')
        qr_buf.seek(0)
        
        # Moldura e QR Code no canto inferior direito do cartão
        c.setFillColor(colors.white)
        c.roundRect(6.6*cm, 0.4*cm, 1.5*cm, 1.5*cm, 2, fill=1, stroke=0)
        c.drawImage(ImageReader(qr_buf), 6.65*cm, 0.45*cm, width=1.4*cm, height=1.4*cm)
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica-Bold", 4.5)
        c.drawCentredString(7.35*cm, 0.2*cm, "VALIDAR SIGAD")
    except Exception as eqr:
        print(f"Aviso QR code cartao: {eqr}")

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
    c.drawCentredString(4.5*cm, 0.4*cm, "Pastor Presidente")
    c.setStrokeColor(colors.HexColor("#475569"))
    c.line(2.8*cm, 0.65*cm, 6.2*cm, 0.65*cm)

    c.showPage()
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"Cartao_Membro_{m['nome'].replace(' ', '_')}.pdf", mimetype="application/pdf")

@app.route('/membro/certificado_pdf/<int:id>/<tipo>')
def certificado_membro_pdf(id, tipo):
    if not can_cadastro(): return redirect('/')
    conn = get_db()
    m = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not m: return redirect('/')

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
    if not can_tesouraria(): return redirect('/')
    conn = get_db()
    f = conn.execute("SELECT * FROM financeiro WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not f: return redirect('/')

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
    if not can_tesouraria(): return redirect('/')
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
    if not is_admin(): return redirect('/')
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
    if not can_tesouraria(): return redirect('/')
    data_raw = request.form.get('data_movimento') or datetime.now().strftime("%Y-%m-%d")
    dt_obj = datetime.strptime(data_raw, "%Y-%m-%d")
    conn = get_db()
    metodo = request.form.get('metodo_pagamento', 'Dinheiro')
    referencia = request.form.get('referencia_transacao', '').strip() or None

    # Auto-cura: Garantir que as colunas existam na tabela antes de inserir
    try:
        conn.execute("ALTER TABLE financeiro ADD COLUMN metodo_pagamento TEXT DEFAULT 'Dinheiro'")
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute("ALTER TABLE financeiro ADD COLUMN referencia_transacao TEXT")
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao, metodo_pagamento, referencia_transacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                      request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                      datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao'], metodo, referencia))
        conn.commit()
    except Exception as e:
        # Fallback de seguranca caso ocorra qualquer restricao com as novas colunas
        conn.execute('''INSERT INTO financeiro (tipo, local_movimento, departamento, categoria, valor, data_movimento, dia, mes, ano, data_registo, membro_id, descricao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (request.form['tipo'], request.form.get('local_movimento', 'Caixa'), request.form.get('departamento', 'Geral'),
                      request.form['categoria'], float(request.form['valor']), dt_obj.strftime("%d/%m/%Y"), dt_obj.day, dt_obj.month, dt_obj.year,
                      datetime.now().strftime("%d/%m/%Y %H:%M"), request.form.get('membro_id') or None, request.form['descricao']))
        conn.commit()
    finally:
        conn.close()
    return redirect('/')

@app.route('/financeiro/transferir', methods=['POST'])
def transferir_fundos():
    if not can_tesouraria(): return redirect('/')
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
    return redirect('/')

@app.route('/casamentos/novo', methods=['POST'])
def novo_casamento():
    if not can_cadastro(): return redirect('/')
    conn = get_db()
    conn.execute('''INSERT INTO casamentos (noivo, noiva, data_casamento, pastor_oficiante, data_registo)
                    VALUES (?, ?, ?, ?, ?)''',
                 (request.form['noivo'], request.form['noiva'], request.form['data_casamento'],
                  request.form.get('pastor_oficiante', ''), datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/mortes/novo', methods=['POST'])
def novo_morte():
    if not can_cadastro(): return redirect('/')
    conn = get_db()
    conn.execute('''INSERT INTO mortes (nome_falecido, data_falecimento, observacoes, data_registo)
                    VALUES (?, ?, ?, ?)''',
                 (request.form['nome_falecido'], request.form['data_falecimento'],
                  request.form.get('observacoes', ''), datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/usuarios/novo', methods=['POST'])
def novo_usuario():
    if not is_admin(): return redirect('/')
    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    m_id_form = request.form.get('membro_id')
    m_id_val = int(m_id_form) if (m_id_form and m_id_form.isdigit()) else None
    prof_id_form = request.form.get('professor_id')
    prof_id_val = int(prof_id_form) if (prof_id_form and prof_id_form.isdigit()) else None
    prof_nome_val = (request.form.get('professor_nome') or '').strip()

    if prof_nome_val and m_id_val:
        try:
            conn_p = get_db()
            param_ch = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            conn_p.execute(f"UPDATE membros SET professor_id = {param_ch}, professor_nome = {param_ch} WHERE id = {param_ch}", (prof_id_val, prof_nome_val, m_id_val))
            conn_p.commit()
        except Exception as e:
            print("Erro ao alocar professor ao membro:", e)

    if user and senha:
        conn = get_db()
        try:
            try:
                conn.execute("ALTER TABLE usuarios ADD COLUMN membro_id INTEGER")
                conn.commit()
            except Exception:
                pass

            param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            if m_id_val:
                conn.execute(f"INSERT INTO usuarios (usuario, senha, cargo, membro_id) VALUES ({param_char}, {param_char}, {param_char}, {param_char})", (user, senha, cargo, m_id_val))
            else:
                conn.execute(f"INSERT INTO usuarios (usuario, senha, cargo) VALUES ({param_char}, {param_char}, {param_char})", (user, senha, cargo))
            conn.commit()
            session['sucesso_cadastro'] = f"Utilizador '{user}' criado com sucesso!"
        except Exception:
            session['alerta_duplicado'] = f"Utilizador '{user}' já existe."
        conn.close()
    return redirect('/')

@app.route('/usuarios/apagar/<int:id>')
def apagar_usuario(id):
    if not is_admin(): return redirect('/')
    conn = get_db()
    u = conn.execute("SELECT usuario FROM usuarios WHERE id = ?", (id,)).fetchone()
    if u and u['usuario'] != 'admin':
        conn.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect('/')

@app.route('/apagar/<tabela>/<int:id>')
def apagar_registo(tabela, id):
    if not is_admin(): return redirect('/')
    mapa = {'membro': ('membros', 'id'), 'financeiro': ('financeiro', 'id'), 'casamento': ('casamentos', 'id'), 'morte': ('mortes', 'id'), 'patrimonio': ('patrimonio', 'id'), 'escala': ('escalas', 'id'), 'culto': ('cultos_frequencia', 'id'), 'convertido': ('novos_convertidos', 'id')}
    if tabela in mapa:
        tab, col = mapa[tabela]
        conn = get_db()
        conn.execute(f"DELETE FROM {tab} WHERE {col} = ?", (id,))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/config/departamento/novo', methods=['POST'])
def novo_depto():
    if not is_admin(): return redirect('/')
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
    return redirect('/')

@app.route('/config/departamento/apagar/<int:id>')
def apagar_depto(id):
    if not is_admin(): return redirect('/')
    conn = get_db()
    conn.execute("DELETE FROM departamentos_lista WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/config/categoria/novo', methods=['POST'])
def nova_categoria():
    if not is_admin(): return redirect('/')
    tipo, nome = request.form.get('tipo'), request.form.get('nome', '').strip()
    if tipo and nome:
        conn = get_db()
        conn.execute("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", (tipo, nome))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/config/categoria/apagar/<int:id>')
def apagar_categoria(id):
    if not is_admin(): return redirect('/')
    conn = get_db()
    conn.execute("DELETE FROM categorias_financeiras WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/config/zona/novo', methods=['POST'])
def nova_zona():
    if not is_admin(): return redirect('/')
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
    return redirect('/')

@app.route('/config/zona/apagar/<int:id>')
def apagar_zona(id):
    if not is_admin(): return redirect('/')
    conn = get_db()
    conn.execute("DELETE FROM zonas_lista WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/exportar/financeiro')
def exportar_financeiro():
    if not can_tesouraria(): return redirect('/')
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
    if not can_cadastro(): return redirect('/')
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
        return redirect('/')
    
    resposta = request.form.get('resposta', '').strip()
    if resposta:
        conn = get_db()
        param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
        conn.execute(f"UPDATE duvidas_estudantes SET resposta = {param_char} WHERE id = {param_char}", (resposta, id))
        conn.commit()
        conn.close()
        session['sucesso_cadastro'] = "Resposta pastoral enviada com sucesso para a sala de aula do aluno!"
    
    return redirect('/')


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
from reportlab.lib.utils import ImageReader
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
                                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-white text-dark border px-3 py-2 fw-semibold">Lição {{ lid + 1 }} de {{ total_licoes }}</span>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-sm btn-success fw-bold">🎓 Certificado</a>
                    {% endif %}
                    <a href="/logout" class="btn btn-sm btn-outline-danger fw-bold px-3 py-1 shadow-sm d-flex align-items-center gap-1" title="Encerrar sessão e voltar ao login">
                        <span>🚪</span> Sair da Sala
                    </a>
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
                <div class="card-header-prova d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <div>
                        <h3 class="fw-bold mb-1">📝 Prova de Avaliação</h3>
                        <div class="text-light">{{ classe.nome }} • Questionário Oficial</div>
                    </div>
                    <div>
                        <a href="/logout" class="btn btn-sm btn-outline-light fw-bold px-3 py-2 shadow-sm d-flex align-items-center gap-1">
                            <span>🚪</span> Sair da Sala
                        </a>
                    </div>
                </div>
                <div class="card-body p-4 p-md-5">
                    <form id="formAvaliacao" action="/discipulado/avaliar/{{ cid }}" method="POST">
                        <input type="hidden" name="membro_id" value="{{ membro_id_aluno }}">
                        
                        <div class="alert alert-primary d-flex align-items-center mb-4 p-3 rounded-3" style="font-size: 0.95rem;">
                            <span class="me-2 fs-5">👤</span>
                            <div><strong>Candidato / Aluno:</strong> {{ nome_aluno_ativo }}</div>
                        </div>

                        {% for q in classe.questionario %}
                        <div class="mb-4 pb-3 border-bottom questao-bloco" id="bloco_q_{{ q.id }}">
                            <p class="fw-bold text-dark mb-2" style="font-size: 1.05rem;">{{ loop.index }}. {{ q.pergunta }}</p>
                            {% for op in q.opcoes %}
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="resp_{{ q.id }}" value="{{ loop.index0 }}" id="q_{{ q.id }}_{{ loop.index0 }}">
                                <label class="form-check-label text-secondary" for="q_{{ q.id }}_{{ loop.index0 }}" style="font-size: 1rem;">{{ op }}</label>
                            </div>
                            {% endfor %}
                            <div class="text-danger small mt-1 d-none aviso-obrigatorio" id="aviso_q_{{ q.id }}">⚠️ Por favor, selecione uma resposta para esta pergunta antes de submeter.</div>
                        </div>
                        {% endfor %}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="/discipulado/classe/{{ cid }}/licao/0" class="btn btn-outline-secondary">« Rever Lições</a>
                            <button type="submit" id="btnSubmeter" class="btn btn-primary fw-bold px-4 py-3 rounded-3 shadow">
                                <span>Submeter Respostas e Concluir Classe »</span>
                            </button>
                        </div>
                    </form>

                    <script>
                    document.getElementById('formAvaliacao').addEventListener('submit', function(e) {
                        var questoes = document.querySelectorAll('.questao-bloco');
                        var primeiraNaoRespondida = null;

                        questoes.forEach(function(bloco) {
                            var radios = bloco.querySelectorAll('input[type="radio"]');
                            var respondida = false;
                            radios.forEach(function(r) { if(r.checked) respondida = true; });
                            
                            var aviso = bloco.querySelector('.aviso-obrigatorio');
                            if (!respondida) {
                                if (aviso) aviso.classList.remove('d-none');
                                if (!primeiraNaoRespondida) primeiraNaoRespondida = bloco;
                            } else {
                                if (aviso) aviso.classList.add('d-none');
                            }
                        });

                        if (primeiraNaoRespondida) {
                            e.preventDefault();
                            primeiraNaoRespondida.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            return false;
                        }

                        var btn = document.getElementById('btnSubmeter');
                        btn.disabled = true;
                        btn.innerHTML = '<span>⏳ A processar notas...</span>';
                    });
                    </script>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Identificar aluno pela sessao
    usuario_sessao = session.get('usuario', '')
    nome_aluno = usuario_sessao or 'Candidato IEAD'
    m_id_ativo = 1
    
    try:
        conn_aluno = get_db_connection()
        cur_aluno = conn_aluno.cursor()
        cur_aluno.execute("SELECT id, nome FROM membros WHERE LOWER(TRIM(nome)) LIKE LOWER(?) OR LOWER(TRIM(telefone)) = LOWER(?)", (f"%{usuario_sessao}%", usuario_sessao))
        m_row = cur_aluno.fetchone()
        if m_row:
            m_id_ativo = m_row[0] if isinstance(m_row, (tuple, list)) else m_row['id']
            nome_aluno = m_row[1] if isinstance(m_row, (tuple, list)) else m_row['nome']
        conn_aluno.close()
    except Exception:
        pass

    return render_template_string(html, classe=classe, cid=cid, membro_id_aluno=m_id_ativo, nome_aluno_ativo=nome_aluno)


@app.route('/discipulado/avaliar/<cid>', methods=['POST'])
def processar_avaliacao_discipulado(cid):
    if cid not in CURRICULO_CLASSES:
        return "Classe inválida", 400

    from flask import request, render_template_string, session

    classe = CURRICULO_CLASSES[cid]
    m_id = request.form.get('membro_id')
    if not m_id:
        # Tenta pegar da sessao ou do primeiro membro cadastrado
        m_id = session.get('membro_id')
    
    if not m_id:
        try:
            conn_temp = get_db_connection()
            cur_temp = conn_temp.cursor()
            cur_temp.execute("SELECT id FROM membros ORDER BY id ASC LIMIT 1")
            row_primeiro = cur_temp.fetchone()
            conn_temp.close()
            if row_primeiro:
                m_id = row_primeiro[0] if isinstance(row_primeiro, (tuple, list)) else row_primeiro['id']
            else:
                m_id = 1
        except Exception:
            m_id = 1
    try:
        m_id = int(m_id)
    except Exception:
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

    # Gravar progresso de forma segura (Compatível com PostgreSQL e SQLite)
    try:
        conn = get_db_connection()
        c = conn.cursor()
        is_pg = bool(DATABASE_URL and psycopg2)

        if is_pg:
            c.execute("""
                CREATE TABLE IF NOT EXISTS progresso_discipulado (
                    id SERIAL PRIMARY KEY,
                    membro_id INTEGER,
                    classe_id TEXT,
                    nota REAL,
                    status TEXT,
                    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Atualiza se ja existir para essa classe, ou insere novo
            c.execute("""
                DELETE FROM progresso_discipulado WHERE membro_id = %s AND classe_id = %s
            """, (m_id, cid))
            c.execute("""
                INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
                VALUES (%s, %s, %s, %s)
            """, (m_id, cid, nota_final, status))
        else:
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
                DELETE FROM progresso_discipulado WHERE membro_id = ? AND classe_id = ?
            """, (m_id, cid))
            c.execute("""
                INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
                VALUES (?, ?, ?, ?)
            """, (m_id, cid, nota_final, status))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar progresso do discipulado: {e}")

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

def migrar_banco_imediato():
    try:
        conn = get_db_connection() if 'get_db_connection' in globals() else get_db()
        c = conn.cursor() if hasattr(conn, 'cursor') else conn
        colunas = [
            ("zona", "VARCHAR(150)"),
            ("celula", "VARCHAR(150)"),
            ("bairro", "VARCHAR(150)"),
            ("distrito", "VARCHAR(150)"),
            ("estado", "VARCHAR(50) DEFAULT 'Activo'")
        ]
        for col, tipo in colunas:
            try:
                c.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                conn.commit()
            except Exception:
                if hasattr(conn, 'rollback'): conn.rollback()
        conn.close()
    except Exception as err:
        print(f"Aviso migracao: {err}")

try:
    migrar_banco_imediato()
except Exception:
    pass


def criar_tabelas_faltantes():
    try:
        conn = get_db_connection() if 'get_db_connection' in globals() else get_db()
        c = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = bool(DATABASE_URL and psycopg2)

        # Tabela zonas_lista
        if is_pg:
            c.execute("""
                CREATE TABLE IF NOT EXISTS zonas_lista (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE NOT NULL
                );
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS zonas_lista (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL
                );
            """)

        # Tabela avaliacoes_estudantes se faltar
        if is_pg:
            c.execute("""
                CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
                    id SERIAL PRIMARY KEY,
                    usuario VARCHAR(150),
                    licao VARCHAR(50),
                    nota INTEGER,
                    total INTEGER,
                    data_resposta VARCHAR(50)
                );
            """)
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    licao TEXT,
                    nota INTEGER,
                    total INTEGER,
                    data_resposta TEXT
                );
            """)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso criacao tabelas: {e}")

try:
    criar_tabelas_faltantes()
except Exception:
    pass


# ==========================================================
# ROTAS SUPERADMIN (GESTAO DE TODAS AS IGREJAS)
# ==========================================================
@app.route('/superadmin/igrejas', methods=['GET', 'POST'])
def superadmin_igrejas():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito ao Super Administrador.", "erro")
        return redirect('/')
    
    conn = get_db()
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        cidade = (request.form.get('cidade') or '').strip()
        distrito = (request.form.get('distrito') or '').strip()
        pastor = (request.form.get('pastor') or '').strip()
        telefone = (request.form.get('telefone') or '').strip()
        
        # Dados do primeiro utilizador da congregação
        admin_user = (request.form.get('admin_user') or '').strip()
        admin_pass = (request.form.get('admin_pass') or '').strip()
        
        if nome:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO igrejas (nome, cidade, distrito, pastor, telefone, ativa)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (nome, cidade, distrito, pastor, telefone))
                nova_igreja_id = cur.lastrowid
                
                if admin_user and admin_pass:
                    cur.execute("""
                        INSERT INTO usuarios (usuario, senha, cargo, igreja_id, is_superadmin)
                        VALUES (?, ?, 'Pastor', ?, 0)
                    """, (admin_user, admin_pass, nova_igreja_id))
                
                conn.commit()
                flash(f"Congregação '{nome}' criada com sucesso!", "sucesso")
            except Exception as e:
                flash(f"Erro ao criar congregação: {e}", "erro")
        return redirect(url_for('superadmin_igrejas'))
        
    igrejas = conn.execute("""
        SELECT i.*, 
               (SELECT COUNT(*) FROM membros m WHERE m.igreja_id = i.id) as total_membros,
               (SELECT COUNT(*) FROM usuarios u WHERE u.igreja_id = i.id) as total_usuarios
        FROM igrejas i
        ORDER BY i.id ASC
    """).fetchall()
    conn.close()
    return render_template('superadmin_igrejas.html', igrejas=igrejas)


@app.route('/superadmin/estatisticas')
def superadmin_estatisticas():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito ao Super Administrador.", "erro")
        return redirect('/')
    
    conn = get_db()
    
    # Lista de igrejas com estatísticas consolidadas
    igrejas = conn.execute("SELECT * FROM igrejas ORDER BY id ASC").fetchall()
    stats_igrejas = []
    
    total_membros_geral = 0
    total_entradas_geral = 0.0
    total_saidas_geral = 0.0
    
    for ig in igrejas:
        ig_id = ig['id']
        membros_count = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (ig_id,)).fetchone()[0]
        entradas = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Entrada' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        saidas = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Saida' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        
        saldo = float(entradas) - float(saidas)
        total_membros_geral += membros_count
        total_entradas_geral += float(entradas)
        total_saidas_geral += float(saidas)
        
        stats_igrejas.append({
            'id': ig['id'],
            'nome': ig['nome'],
            'cidade': ig['cidade'],
            'distrito': ig['distrito'],
            'pastor': ig['pastor'],
            'telefone': ig['telefone'],
            'ativa': ig['ativa'],
            'total_membros': membros_count,
            'total_entradas': float(entradas),
            'total_saidas': float(saidas),
            'saldo': saldo
        })
        
    conn.close()
    
    saldo_geral = total_entradas_geral - total_saidas_geral
    
    return render_template(
        'superadmin_estatisticas.html',
        total_igrejas=len(igrejas),
        total_membros_geral=total_membros_geral,
        total_entradas_geral=total_entradas_geral,
        total_saidas_geral=total_saidas_geral,
        saldo_geral=saldo_geral,
        stats_igrejas=stats_igrejas
    )

@app.route('/superadmin/estatisticas/pdf')
def superadmin_estatisticas_pdf():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito.", "erro")
        return redirect('/')
        
    conn = get_db()
    igrejas = conn.execute("SELECT * FROM igrejas ORDER BY id ASC").fetchall()
    
    dados_tabela = [["Congregação", "Pastor Titular", "Membros", "Entradas (MT)", "Saídas (MT)", "Saldo (MT)"]]
    tot_membros = 0
    tot_ent = 0.0
    tot_sai = 0.0
    
    for ig in igrejas:
        ig_id = ig['id']
        m_cnt = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (ig_id,)).fetchone()[0]
        e = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Entrada' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        s = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Saida' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        sal = float(e) - float(s)
        
        tot_membros += m_cnt
        tot_ent += float(e)
        tot_sai += float(s)
        
        dados_tabela.append([
            ig['nome'][:20],
            (ig['pastor'] or '-')[:18],
            str(m_cnt),
            f"{float(e):,.2f}",
            f"{float(s):,.2f}",
            f"{sal:,.2f}"
        ])
    conn.close()
    
    # Linha Total
    dados_tabela.append([
        "TOTAL GERAL",
        "-",
        str(tot_membros),
        f"{tot_ent:,.2f}",
        f"{tot_sai:,.2f}",
        f"{(tot_ent - tot_sai):,.2f}"
    ])
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1)),
        Paragraph("<font size=10 color='#475569'><b>SISTEMA INTEGRADO DE GESTÃO ECLESIÁSTICA (SIGAD)</b></font>", ParagraphStyle('H2', alignment=1)),
        Spacer(1, 0.4*cm),
        Paragraph("<b>RELATÓRIO ESTATÍSTICO E CONSOLIDADO DE TODAS AS CONGREGAÇÕES</b>", ParagraphStyle('H3', alignment=1)),
        Spacer(1, 0.5*cm)
    ]
    
    t = Table(dados_tabela, colWidths=[4.2*cm, 3.8*cm, 2.0*cm, 2.8*cm, 2.8*cm, 2.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elementos.append(t)
    
    elementos.append(Spacer(1, 1.2*cm))
    elementos.append(Paragraph("____________________________________________<br/><b>Secretaria Geral e Superintendência Nacional</b>", ParagraphStyle('Ass', alignment=1, fontSize=9)))
    
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="Relatorio_Consolidado_SIGAD.pdf", mimetype='application/pdf')


# ================= ROTA DE GESTÃO DO FUNIL DE DISCIPULADO =================
@app.route('/discipulado/atualizar_fase', methods=['POST'])
def atualizar_fase_discipulado():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    membro_id = request.form.get('membro_id')
    nova_fase = request.form.get('nova_fase')
    discipulador = request.form.get('discipulador', '').strip()
    data_batismo = request.form.get('data_batismo', '').strip()
    
    conn = get_db()
    if nova_fase == 'Batizado' and data_batismo:
        conn.execute("""
            UPDATE membros 
            SET fase_discipulado = ?, discipulador = COALESCE(NULLIF(?, ''), discipulador), data_batismo = ?
            WHERE id = ?
        """, (nova_fase, discipulador, data_batismo, membro_id))
    else:
        conn.execute("""
            UPDATE membros 
            SET fase_discipulado = ?, discipulador = COALESCE(NULLIF(?, ''), discipulador)
            WHERE id = ?
        """, (nova_fase, discipulador, membro_id))
        
    conn.commit()
    conn.close()
    flash("Fase de discipulado atualizada com sucesso!", "sucesso")
    return redirect('/#secao-discipulado')

@app.route('/secretaria/relatorio_oficial')
def ver_relatorio_oficial():
    conn = get_db()
    membros = []
    cultos = []
    planos = []
    casamentos = []
    
    try:
        membros = conn.execute("SELECT * FROM membros").fetchall()
    except Exception:
        pass
        
    try:
        cultos = conn.execute("SELECT * FROM cultos_frequencia ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    try:
        planos = conn.execute("SELECT * FROM actividades_planeamento ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    try:
        casamentos = conn.execute("SELECT * FROM casamentos ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    conn.close()
    return render_template('relatorio_oficial_modelo.html', membros=membros, cultos=cultos, planos=planos, casamentos=casamentos)


@app.route('/secretaria/dashboard_membros')
def dashboard_membros():
    conn = get_db()
    membros = []
    try:
        # Garante a existência da coluna no PostgreSQL/SQLite
        try:
            conn.execute("ALTER TABLE membros ADD COLUMN estado_civil TEXT DEFAULT 'Solteiro(a)'")
            conn.commit()
        except: pass
        membros = conn.execute("SELECT * FROM membros").fetchall()
    except Exception as e:
        print("Erro ao ler membros:", e)
        membros = []
    finally:
        conn.close()

    total = len(membros)
    homens = 0
    mulheres = 0
    batizados = 0
    nao_batizados = 0
    novos_convertidos = 0

    faixa_criancas = {'H': 0, 'M': 0}      # 0 a 13 anos
    faixa_adolescentes = {'H': 0, 'M': 0}  # 14 a 17 anos
    faixa_jovens = {'H': 0, 'M': 0}        # 18 a 35 anos
    faixa_adultos = {'H': 0, 'M': 0}       # 36 a 59 anos
    faixa_terceira = {'H': 0, 'M': 0}      # 60+ anos

    obreiros_contagem = {'Pastores': 0, 'Presbíteros': 0, 'Evangelistas': 0, 'Diáconos': 0}
    estado_civil = {}
    departamentos = {}

    ano_atual = datetime.now().year

    for m in membros:
        item = dict(m) if hasattr(m, 'keys') else m

        # 1. Género
        raw_gen = str(item.get('genero') or item.get('sexo') or '').strip().lower()
        if raw_gen.startswith('f') or 'mulher' in raw_gen:
            gen = 'M'
            mulheres += 1
        else:
            gen = 'H'
            homens += 1

        # 2. Baptismo / Novos Convertidos
        dt_batismo = str(item.get('data_batismo') or '').strip()
        posicao = str(item.get('posicao_atual') or item.get('cargo_lideranca') or '').strip().lower()
        ano_conv = str(item.get('ano_conv') or '').strip()

        if dt_batismo and dt_batismo.lower() not in ['none', 'null', 'nan', '']:
            batizados += 1
        elif 'convertid' in posicao or (ano_conv and ano_conv == str(ano_atual)):
            novos_convertidos += 1
        else:
            nao_batizados += 1

        # 3. Faixas Etárias
        dn = str(item.get('data_nasc') or item.get('data_nascimento') or '').strip()
        segmento = str(item.get('segmento') or '').strip().lower()
        
        idade = None
        try:
            if '-' in dn:
                partes = dn.split('-')
                ano_nasc = int(partes[0]) if len(partes[0]) == 4 else int(partes[2])
                idade = ano_atual - ano_nasc
            elif '/' in dn:
                partes = dn.split('/')
                ano_nasc = int(partes[2]) if len(partes) >= 3 else 1990
                idade = ano_atual - ano_nasc
        except Exception:
            idade = None

        if idade is not None:
            if idade <= 13: faixa_criancas[gen] += 1
            elif 14 <= idade <= 17: faixa_adolescentes[gen] += 1
            elif 18 <= idade <= 35: faixa_jovens[gen] += 1
            elif 36 <= idade <= 59: faixa_adultos[gen] += 1
            else: faixa_terceira[gen] += 1
        else:
            if 'criança' in segmento: faixa_criancas[gen] += 1
            elif 'adolescente' in segmento: faixa_adolescentes[gen] += 1
            elif 'jovem' in segmento: faixa_jovens[gen] += 1
            elif 'idoso' in segmento or 'terceira' in segmento: faixa_terceira[gen] += 1
            else: faixa_adultos[gen] += 1

        # 4. Obreiros
        if 'pastor' in posicao: obreiros_contagem['Pastores'] += 1
        elif 'presb' in posicao: obreiros_contagem['Presbíteros'] += 1
        elif 'evang' in posicao: obreiros_contagem['Evangelistas'] += 1
        elif 'diac' in posicao: obreiros_contagem['Diáconos'] += 1

        # 5. Departamento
        dep = str(item.get('departamento') or 'Geral').strip()
        if not dep or dep.lower() in ['none', 'null', 'nan']: dep = 'Geral'
        departamentos[dep] = departamentos.get(dep, 0) + 1

        # 6. Estado Civil Real
        ec = str(item.get('estado_civil') or '').strip()
        if not ec or ec.lower() in ['none', 'null', 'nan']:
            ec = 'Não Informado'
        estado_civil[ec] = estado_civil.get(ec, 0) + 1

    perc_homens = round((homens / total * 100), 1) if total > 0 else 0
    perc_mulheres = round((mulheres / total * 100), 1) if total > 0 else 0

    dados_dashboard = {
        'total': total,
        'homens': homens,
        'mulheres': mulheres,
        'perc_homens': perc_homens,
        'perc_mulheres': perc_mulheres,
        'batizados': batizados,
        'nao_batizados': nao_batizados,
        'novos_convertidos': novos_convertidos,
        'faixa_criancas': faixa_criancas,
        'faixa_adolescentes': faixa_adolescentes,
        'faixa_jovens': faixa_jovens,
        'faixa_adultos': faixa_adultos,
        'faixa_terceira': faixa_terceira,
        'obreiros': obreiros_contagem,
        'departamentos': departamentos,
        'estado_civil': estado_civil
    }

    return render_template('dashboard_membros.html', d=dados_dashboard)



# --- ROTAS DE CONFIGURAÇÃO ECLESIÁSTICA EXPANDIDA ---
@app.route('/config/cargo/novo', methods=['POST'])
def config_cargo_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_cargos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/cargo/apagar/<int:id>')
def config_cargo_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_cargos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/culto/novo', methods=['POST'])
def config_culto_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_cultos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/culto/apagar/<int:id>')
def config_culto_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_cultos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/conta/novo', methods=['POST'])
def config_conta_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_contas (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/conta/apagar/<int:id>')
def config_conta_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_contas WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/atividade/novo', methods=['POST'])
def config_atividade_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_atividades (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/atividade/apagar/<int:id>')
def config_atividade_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_atividades WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/igreja/nova', methods=['POST'])
def config_igreja_nova():
    prov = request.form.get('provincia', '').strip()
    dist = request.form.get('distrito', '').strip()
    nome = request.form.get('nome', '').strip()
    if prov and dist and nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO igrejas_distritos (provincia, distrito, nome) VALUES (?, ?, ?)", (prov, dist, nome))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/igreja/apagar/<int:id>')
def config_igreja_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM igrejas_distritos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')


@app.route('/config/evento/novo', methods=['POST'])
def config_evento_novo():
    nome = request.form.get('nome', '').strip()
    if nome:
        conn = get_db()
        try:
            conn.execute("INSERT INTO config_eventos (nome) VALUES (?)", (nome,))
            conn.commit()
        except: pass
        finally: conn.close()
    return redirect('/?tab=configuracoes')

@app.route('/config/evento/apagar/<int:id>')
def config_evento_apagar(id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM config_eventos WHERE id = ?", (id,))
        conn.commit()
    except: pass
    finally: conn.close()
    return redirect('/?tab=configuracoes')


# =======================================================
# ROTA TEMPORÁRIA: REDEFINIR SENHA ADMIN NA NUVEM
# =======================================================
@app.route('/redefinir_senha_urgente_admin_2026')
def redefinir_senha_urgente_admin():
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = bool(DATABASE_URL and psycopg2)
        param = "%s" if is_pg else "?"
        
        # Redefine a senha do admin para: admin123
        cur.execute(f"UPDATE usuarios SET senha = {param} WHERE usuario = {param}", ('admin123', 'admin'))
        conn.commit()
        if hasattr(conn, 'close'):
            conn.close()
            
        return '''
        <div style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1 style="color: #15803d;">✓ Senha Redefinida com Sucesso no Render!</h1>
            <p style="font-size: 18px;">Utilizador: <b>admin</b></p>
            <p style="font-size: 18px;">Nova Palavra-passe: <b style="background: #fef08a; padding: 4px 8px; border-radius: 4px;">admin123</b></p>
            <br><br>
            <a href="/login" style="background: #0d3b66; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Ir para o Login</a>
        </div>
        '''
    except Exception as e:
        return f"<h3>Erro ao redefinir: {e}</h3>"


# =======================================================
# MÓDULO DE RECUPERAÇÃO DE PALAVRA-PASSE (ADMIN)
# =======================================================
import random
import time

# Armazena temporariamente códigos de verificação em memória
# Formato: {'email': {'codigo': '123456', 'expira': timestamp}}
CODIGOS_RECUPERACAO = {}
EMAIL_ADMIN_AUTORIZADO = "almunguame@gmail.com"

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    msg_erro = None
    msg_sucesso = None
    
    if request.method == 'POST':
        email_digitado = (request.form.get('email') or '').strip().lower()
        
        if email_digitado == EMAIL_ADMIN_AUTORIZADO.lower():
            # Gera código aleatório de 6 dígitos
            codigo = f"{random.randint(100000, 999999)}"
            CODIGOS_RECUPERACAO[email_digitado] = {
                'codigo': codigo,
                'expira': time.time() + 900  # 15 minutos
            }
            session['email_reset'] = email_digitado
            # Redireciona para a tela de confirmação
            return redirect('/confirmar-codigo-recuperacao')
        else:
            msg_erro = "E-mail não reconhecido como administrador autorizado do sistema."
            
    return render_template('esqueci_senha.html', msg_erro=msg_erro)


@app.route('/confirmar-codigo-recuperacao', methods=['GET', 'POST'])
def confirmar_codigo_recuperacao():
    email = session.get('email_reset')
    if not email or email not in CODIGOS_RECUPERACAO:
        return redirect('/esqueci-senha')
        
    dados_codigo = CODIGOS_RECUPERACAO[email]
    codigo_ativo = dados_codigo['codigo']
    msg_erro = None
    
    if request.method == 'POST':
        codigo_informado = (request.form.get('codigo') or '').strip()
        nova_senha = (request.form.get('nova_senha') or '').strip()
        confirmar_senha = (request.form.get('confirmar_senha') or '').strip()
        
        if time.time() > dados_codigo['expira']:
            msg_erro = "O código expirou. Solicite um novo código."
        elif codigo_informado != codigo_ativo:
            msg_erro = "Código de confirmação incorreto. Verifique atentamente."
        elif len(nova_senha) < 4:
            msg_erro = "A nova palavra-passe deve conter pelo menos 4 caracteres."
        elif nova_senha != confirmar_senha:
            msg_erro = "As palavras-passe digitadas não coincidem."
        else:
            # Atualiza no Banco de Dados
            try:
                conn = get_db()
                cur = conn.cursor() if hasattr(conn, 'cursor') else conn
                param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
                cur.execute(f"UPDATE usuarios SET senha = {param} WHERE usuario = {param}", (nova_senha, 'admin'))
                conn.commit()
                if hasattr(conn, 'close'):
                    conn.close()
                del CODIGOS_RECUPERACAO[email]
                session.pop('email_reset', None)
                session['sucesso_login_msg'] = "Palavra-passe do administrador redefinida com sucesso!"
                return redirect('/login')
            except Exception as e:
                msg_erro = f"Erro ao atualizar na base de dados: {e}"

    return render_template('confirmar_codigo.html', email=email, codigo_dica=codigo_ativo, msg_erro=msg_erro)


# =======================================================
# MÓDULO DE CENSO E AUTO-RECENSEAMENTO (PÚBLICO & BRIGADAS)
# =======================================================
import os
from werkzeug.utils import secure_filename

# =======================================================
# MÓDULO DE CENSO E AUTO-RECENSEAMENTO (ALINHADO)
# =======================================================
@app.route('/censo', methods=['GET', 'POST'])
def censo_publico():
    msg_erro = None
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        data_nascimento = request.form.get('data_nascimento')
        genero = request.form.get('genero')
        estado_civil = request.form.get('estado_civil')
        telefone = (request.form.get('telefone') or '').strip()
        bairro = request.form.get('bairro')
        endereco = request.form.get('endereco') or request.form.get('bairro')
        naturalidade = request.form.get('naturalidade')
        filiacao = request.form.get('filiacao')
        tipo_doc = request.form.get('tipo_doc')
        num_doc = request.form.get('num_doc')
        segmento = request.form.get('segmento')
        ano_conversao = request.form.get('ano_conversao')
        batizado = request.form.get('batizado', 'Não')
        cargo = request.form.get('cargo', 'Membro em Comunhão')
        departamento = request.form.get('departamento', 'Geral')
        
        recenseador = session.get('usuario', 'Auto-recenseamento (WhatsApp)')
        
        if not nome or not telefone:
            msg_erro = "Por favor, preencha o Nome Completo e o Contacto telefónico."
            return render_template('censo_form.html', msg_erro=msg_erro)
            
        foto_path = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                nome_foto = f"membro_{int(time.time())}.{ext}"
                caminho_salvar = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), nome_foto)
                os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
                file.save(caminho_salvar)
                foto_path = f"/static/uploads/{nome_foto}"

        try:
            conn = get_db()
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            status_inicial = 'Pendente de Validação'
            
            sql = f'''
                INSERT INTO membros (
                    nome, data_nascimento, genero, estado_civil, telefone,
                    bairro, endereco, naturalidade, filiacao, tipo_doc, num_doc,
                    segmento, ano_conversao, batizado, cargo, departamento,
                    status, foto_path, professor_nome
                ) VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})
            '''
            cur.execute(sql, (
                nome, data_nascimento, genero, estado_civil, telefone,
                bairro, endereco, naturalidade, filiacao, tipo_doc, num_doc,
                segmento, ano_conversao, batizado, cargo, departamento,
                status_inicial, foto_path, recenseador
            ))
            conn.commit()
            if hasattr(conn, 'close'):
                conn.close()
                
            return render_template('censo_sucesso.html', nome=nome, status=status_inicial)
        except Exception as e:
            msg_erro = f"Erro ao registar a ficha: {e}"

    return render_template('censo_form.html', msg_erro=msg_erro)


@app.route('/admin/censo/homologar')
def painel_homologacao_censo():
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    param = "%s" if is_pg else "?"
    
    usuario_nivel = session.get('nivel', '') or session.get('cargo', '')
    usuario_igreja = session.get('igreja', '')
    is_sede = usuario_nivel in ['Superadmin', 'Pastor Presidente', 'Administrador'] or not usuario_igreja
    
    # Filtro opcional selecionado na URL pelo Admin da Sede
    filtro_igreja = request.args.get('igreja_filtro', '')
    
    # Buscar lista de todas as congregações cadastradas
    lista_igrejas = ['IEAD Chicuque']
    try:
        cur.execute("SELECT nome FROM igrejas ORDER BY nome ASC")
        rows = cur.fetchall()
        if rows:
            lista_igrejas = [r[0] for r in rows if r[0]]
            if 'IEAD Chicuque' not in lista_igrejas:
                lista_igrejas.insert(0, 'IEAD Chicuque')
    except Exception:
        pass
    
    # Construir consulta de membros pendentes conforme permissão
    colunas_sql = "id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, igreja, data_cadastro"
    
    if is_sede:
        if filtro_igreja and filtro_igreja != 'Todas':
            query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC"
            cur.execute(query, ('Pendente de Validação', filtro_igreja))
        else:
            query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} ORDER BY id DESC"
            cur.execute(query, ('Pendente de Validação',))
    else:
        # Secretário local: restrito à sua congregação
        query = f"SELECT {colunas_sql} FROM membros WHERE status = {param} AND igreja = {param} ORDER BY id DESC"
        cur.execute(query, ('Pendente de Validação', usuario_igreja))
        
    pendentes = cur.fetchall()
    if hasattr(conn, 'close'):
        conn.close()
        
    return render_template(
        'censo_homologar.html', 
        pendentes=pendentes, 
        is_sede=is_sede, 
        igrejas=lista_igrejas, 
        igreja_atual=filtro_igreja or ('Todas' if is_sede else usuario_igreja),
        usuario_igreja=usuario_igreja
    )


@app.route('/admin/censo/aprovar/<int:membro_id>', methods=['POST'])
def aprovar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"UPDATE membros SET status = {param} WHERE id = {param}", ('Ativo', membro_id))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')


@app.route('/admin/censo/descartar/<int:membro_id>', methods=['POST'])
def descartar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"DELETE FROM membros WHERE id = {param}", (membro_id,))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


def garantir_colunas_membros():
    """Garante que todas as colunas da tabela membros existam no banco ativo"""
    colunas_necessarias = [
        ('endereco', 'TEXT'),
        ('bairro', 'VARCHAR(100)'),
        ('naturalidade', 'VARCHAR(100)'),
        ('filiacao', 'VARCHAR(255)'),
        ('tipo_doc', 'VARCHAR(50)'),
        ('num_doc', 'VARCHAR(100)'),
        ('segmento', 'VARCHAR(50)'),
        ('ano_conversao', 'VARCHAR(50)'),
        ('cargo', 'VARCHAR(100)'),
        ('professor_nome', 'VARCHAR(150)')
    ]
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_postgres = bool(DATABASE_URL and psycopg2)
        
        if is_postgres:
            for col, tipo in colunas_necessarias:
                try:
                    cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
                    conn.commit()
                except Exception:
                    conn.rollback()
        else:
            # SQLite
            cur.execute("PRAGMA table_info(membros);")
            existentes = [linha[1] for linha in cur.fetchall()]
            for col, tipo in colunas_necessarias:
                if col not in existentes:
                    try:
                        cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                        conn.commit()
                    except Exception:
                        pass
        if hasattr(conn, 'close'):
            conn.close()
        print("✓ Estrutura da tabela membros verificada e atualizada com sucesso!")
    except Exception as e:
        print(f"! Aviso na verificação de colunas: {e}")

# Executa ao iniciar o app
try:
    garantir_colunas_membros()
except Exception as e:
    pass
