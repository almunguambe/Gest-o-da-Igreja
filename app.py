import re
import os
def assegurar_tabela_cultos(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cultos (
                id {id_tipo},
                data_culto TEXT,
                tipo_culto TEXT,
                homens_adultos INTEGER DEFAULT 0,
                mulheres_adultas INTEGER DEFAULT 0,
                jovens_rapazes INTEGER DEFAULT 0,
                jovens_mocas INTEGER DEFAULT 0,
                criancas_meninos INTEGER DEFAULT 0,
                criancas_meninas INTEGER DEFAULT 0,
                visitantes_homens INTEGER DEFAULT 0,
                visitantes_mulheres INTEGER DEFAULT 0,
                apelos INTEGER DEFAULT 0,
                total_presentes INTEGER DEFAULT 0,
                pregador TEXT,
                tema_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e_c:
        try:
            if hasattr(conn, 'rollback'): conn.rollback()
        except: pass

def assegurar_tabela_planificacoes(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_col = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS planificacoes (
                id {id_col},
                departamento TEXT,
                tipo_evento TEXT,
                nome_actividade TEXT,
                data_prevista TEXT,
                frequencia TEXT,
                responsavel_directo TEXT,
                contacto TEXT,
                status TEXT DEFAULT 'Pendente'
            );
        """)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception:
        try:
            if hasattr(conn, 'rollback'): conn.rollback()
        except Exception: pass

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
    from psycopg2.extras import DictCursor
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

def _val(row):
    if row is None:
        return 0
    if isinstance(row, dict):
        return list(row.values())[0]
    return row[0]

import json
_original_dumps = json.dumps
def _custom_dumps(*args, **kwargs):
    if 'default' not in kwargs:
        kwargs['default'] = str
    return _original_dumps(*args, **kwargs)
json.dumps = _custom_dumps


def criar_tabela_planificacoes_se_faltar(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
        if is_pg:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id SERIAL PRIMARY KEY,
                    departamento VARCHAR(150),
                    tipo_evento VARCHAR(150),
                    nome_actividade VARCHAR(255),
                    data_prevista VARCHAR(50),
                    frequencia VARCHAR(100),
                    responsavel_directo VARCHAR(150),
                    contacto VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'Pendente'
                );
            ''')
        else:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departamento TEXT,
                    tipo_evento TEXT,
                    nome_actividade TEXT,
                    data_prevista TEXT,
                    frequencia TEXT,
                    responsavel_directo TEXT,
                    contacto TEXT,
                    status TEXT DEFAULT 'Pendente'
                );
            ''')
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()

app = Flask(__name__)

def is_admin():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'superadmin', 'tesoureiro', 'tesouraria', 'secretário', 'secretaria', 'lider', 'líder']



def can_tesouraria():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    # Dá permissão geral aos cargos administrativos para o painel abrir
    return cargo in ['pastor', 'admin', 'superadmin', 'tesoureiro', 'tesouraria', 'secretário', 'secretaria', 'lider', 'líder']



def can_cadastro():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'secretário', 'secretaria', 'secretario', 'tesoureiro', 'tesouraria', 'superadmin']

def can_financeiro():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'tesoureiro', 'tesouraria', 'superadmin']

def can_admin():
    from flask import session
    cargo = str(session.get('cargo', '')).lower()
    return cargo in ['pastor', 'admin', 'superadmin']


import os
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    import os
import sqlite3
import urllib.parse as up

# Suporte nativo a PostgreSQL via pg8000 (compatível com Python 3.14+)
has_postgres = False
try:
    import pg8000.dbapi as pg_driver
    has_postgres = True
except Exception:
    try:
        import psycopg2 as pg_driver
        has_postgres = True
    except Exception:
        pg_driver = None

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

import os

class HybridRow(dict):
    """Permite acesso tanto por chave row['coluna'] quanto por indice row[0]"""
    def __init__(self, cursor, row_values):
        super().__init__()
        self._values = list(row_values)
        for idx, col in enumerate(cursor.description):
            self[col.name] = row_values[idx]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._values[item]
        return super().__getitem__(item)

class HybridCursor:
    def __init__(self, cur, conn):
        self._cur = cur
        self._conn = conn

    def execute(self, sql, params=None):
        # [BLINDAGEM] Limpa o estado da transacao anterior para o PostgreSQL nao travar
        try:
            if hasattr(self, '_conn'):
                self._conn.rollback()
            elif hasattr(self._cur, 'connection'):
                self._cur.connection.rollback()
        except:
            pass

        import re
        if isinstance(sql, str):
            if 'AUTOINCREMENT' in sql.upper():
                sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
                sql = re.sub(r'AUTOINCREMENT', '', sql, flags=re.IGNORECASE)
            if params is not None and '?' in sql:
                sql = sql.replace('?', '%s')
        try:
            if params is not None:
                return self._cur.execute(sql, params)
            return self._cur.execute(sql)
        except Exception as e:
            # Reseta a transação para o próximo comando nunca herdar o estado abortado
            try:
                self._conn.rollback()
            except Exception:
                pass
            if 'CREATE TABLE' in str(sql).upper():
                print(f"[AVISO CREATE TABLE IGNORADO] {e}")
                return None
            raise e

    def fetchone(self):
        try:
            row = self._cur.fetchone()
            return row
        except Exception:
            return None

    def fetchall(self):
        try:
            return self._cur.fetchall()
        except Exception:
            return []

    def __iter__(self):
        try:
            for r in self._cur:
                yield r
        except Exception:
            return iter([])

    def __getattr__(self, name):
        return getattr(self._cur, name)

class HybridConn:
    def __init__(self, conn):
        self._conn = conn
        try:
            self._conn.autocommit = True
        except Exception:
            pass

    def cursor(self):
        return HybridCursor(self._conn.cursor(), self._conn)

    def execute(self, sql, params=None):
        # [BLINDAGEM] Limpa o estado da transacao anterior para o PostgreSQL nao travar
        try:
            if hasattr(self, '_conn'):
                self._conn.rollback()
            elif hasattr(self._cur, 'connection'):
                self._cur.connection.rollback()
        except:
            pass

        c = self.cursor()
        c.execute(sql, params)
        return c

    def commit(self):
        try:
            return self._conn.commit()
        except Exception:
            pass

    def rollback(self):
        try:
            return self._conn.rollback()
        except Exception:
            pass

    def close(self):
        try:
            return self._conn.close()
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._conn, name)

def get_db():
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if db_url:
        try:
            import psycopg2
            raw_conn = psycopg2.connect(db_url)
            raw_conn.autocommit = True
            raw_conn.autocommit = True
            return HybridConn(raw_conn)
        except Exception as e:
            print(f"[ERRO POSTGRES get_db] {e}")


    import sqlite3
    conn = sqlite3.connect("gestao_chicuque.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection():
    return get_db()

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
        # [BLINDAGEM] Limpa o estado da transacao anterior para o PostgreSQL nao travar
        try:
            if hasattr(self, '_conn'):
                self._conn.rollback()
            elif hasattr(self._cur, 'connection'):
                self._cur.connection.rollback()
        except:
            pass

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
        # [BLINDAGEM] Limpa o estado da transacao anterior para o PostgreSQL nao travar
        try:
            if hasattr(self, '_conn'):
                self._conn.rollback()
            elif hasattr(self._cur, 'connection'):
                self._cur.connection.rollback()
        except:
            pass

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
            conn = psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.DictCursor)
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
            CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    nivel TEXT DEFAULT 'admin'
                );
                CREATE TABLE IF NOT EXISTS igrejas (
                id SERIAL PRIMARY KEY,
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
    
    # Detectar se é PostgreSQL real
    is_real_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')

    if is_real_pg:
        # Se for PostgreSQL (Supabase), as tabelas já foram criadas ou usam sintaxe SERIAL
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS igrejas (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL UNIQUE,
                    localizacao TEXT,
                    responsavel TEXT,
                    contacto TEXT
                );
            """)
            conn.commit()
            print("✓ Banco PostgreSQL sincronizado com sucesso!")
        except Exception as e:
            conn.rollback()
            print(f"[ALERTA INIT_DB PG] {e}")
        finally:
            c.close()
            conn.close()
        return

    # Caso seja SQLite local (fallback de desenvolvimento)
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS igrejas (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            localizacao TEXT,
            responsavel TEXT,
            contacto TEXT
        )''')
        conn.commit()
    except Exception as e:
        print(f"[ALERTA INIT_DB SQLITE] {e}")
    finally:
        c.close()
        conn.close()


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

    total_membros = _val(conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (igreja_id,)).fetchone())
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
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
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
    membros_json = json.dumps([dict(m) for m in todos_membros], default=str)

    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)

    # 1. Dúvidas do Discipulado
    duvidas_lista = []
    try:
        cur_duv = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_duv.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
        duvidas_lista = cur_duv.fetchall()
    except Exception:
        duvidas_lista = []

    # 2. Professores do Discipulado (Evita NameError)
    professores_discipulado = []
    try:
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
            if any(term in f_val for term in ['pastor', 'presb', 'diacon', 'evang', 'obreir', 'lider', 'comunh']):
                professores_discipulado.append(m)
        if not professores_discipulado:
            professores_discipulado = todos_membros
    except Exception:
        professores_discipulado = todos_membros if 'todos_membros' in locals() else []

    # 3. Candidatos ao Discipulado
    candidatos_discipulado = []
    try:
        cur_cd = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_cd.execute("""
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
        """)
        candidatos_discipulado = cur_cd.fetchall()
    except Exception:
        candidatos_discipulado = []

    # 4. Leitura Direta de Planificacoes no Dashboard
    planos = []
    try:
        cur_dash_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_dash_pl.execute("SELECT id, departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status FROM planificacoes ORDER BY id DESC")
        linhas_p = cur_dash_pl.fetchall()
        for l in linhas_p:
            if hasattr(l, 'get'):
                item = {
                    'id': l.get('id'),
                    'departamento': l.get('departamento') or 'Geral',
                    'tipo_evento': l.get('tipo_evento') or 'Geral',
                    'nome_actividade': l.get('nome_actividade') or 'Actividade',
                    'data_prevista': l.get('data_prevista') or '---',
                    'frequencia': l.get('frequencia') or 'Pontual',
                    'responsavel_directo': l.get('responsavel_directo') or '---',
                    'contacto': l.get('contacto') or '',
                    'status': l.get('status') or 'Pendente'
                }
            else:
                item = {
                    'id': l[0],
                    'departamento': l[1] or 'Geral',
                    'tipo_evento': l[2] or 'Geral',
                    'nome_actividade': l[3] or 'Actividade',
                    'data_prevista': l[4] or '---',
                    'frequencia': l[5] or 'Pontual',
                    'responsavel_directo': l[6] or '---',
                    'contacto': l[7] or '',
                    'status': l[8] or 'Pendente'
                }
            planos.append(item)
    except Exception as e_p:
        print("[ERRO DASHBOARD PLANIFICACAO]:", e_p)
        planos = []

    # 5. Candidatos ao Batismo
    candidatos_batismo = []
    try:
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
            b_val = str(m.get('batizado', '') if hasattr(m, 'get') else m['batizado'] if 'batizado' in m.keys() else '').lower()
            if ('candidat' in f_val) or ('prova' in f_val) or ('convertid' in f_val) or (b_val in ['nao', 'não', 'pendente', '']):
                candidatos_batismo.append(m)
        if not candidatos_batismo:
            candidatos_batismo = todos_membros
    except Exception:
        candidatos_batismo = todos_membros if 'todos_membros' in locals() else []

    
    # Leitura Universal de Cultos para o Dashboard
    cultos = []
    try:
        assegurar_tabela_cultos(conn)
        cur_clt = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_clt.execute("SELECT id, data_culto, tipo_culto, pregador, tema_mensagem, total_presentes, apelos FROM cultos ORDER BY id DESC LIMIT 50")
        linhas_clt = cur_clt.fetchall()
        for l in linhas_clt:
            if hasattr(l, 'get'):
                cultos.append({
                    'id': l.get('id'),
                    'data_culto': l.get('data_culto') or '---',
                    'tipo_culto': l.get('tipo_culto') or 'Culto',
                    'pregador': l.get('pregador') or '---',
                    'tema_mensagem': l.get('tema_mensagem') or '',
                    'total_presentes': l.get('total_presentes') or 0,
                    'apelos': l.get('apelos') or 0
                })
            else:
                cultos.append({
                    'id': l[0],
                    'data_culto': l[1] or '---',
                    'tipo_culto': l[2] or 'Culto',
                    'pregador': l[3] or '---',
                    'tema_mensagem': l[4] or '',
                    'total_presentes': l[5] or 0,
                    'apelos': l[6] or 0
                })
    except Exception as e_clt:
        print("[AVISO LEITURA CULTOS]:", e_clt)
        cultos = []
    # Leitura Universal de Cultos para o Dashboard
    cultos = []
    try:
        assegurar_tabela_cultos(conn)
        cur_c = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_c.execute("SELECT id, data_culto, tipo_culto, pregador, tema_mensagem, total_presentes, apelos FROM cultos ORDER BY id DESC LIMIT 50")
        linhas_c = cur_c.fetchall()
        for l in linhas_c:
            if hasattr(l, 'get'):
                cultos.append({
                    'id': l.get('id'),
                    'data_culto': l.get('data_culto') or '---',
                    'tipo_culto': l.get('tipo_culto') or 'Culto',
                    'pregador': l.get('pregador') or '---',
                    'tema_mensagem': l.get('tema_mensagem') or '',
                    'total_presentes': l.get('total_presentes') if l.get('total_presentes') is not None else 0,
                    'apelos': l.get('apelos') if l.get('apelos') is not None else 0
                })
            else:
                cultos.append({
                    'id': l[0],
                    'data_culto': l[1] or '---',
                    'tipo_culto': l[2] or 'Culto',
                    'pregador': l[3] or '---',
                    'tema_mensagem': l[4] or '',
                    'total_presentes': l[5] if l[5] is not None else 0,
                    'apelos': l[6] if l[6] is not None else 0
                })
    except Exception as e_c:
        print("[ERRO LEITURA CULTOS]:", e_c)
        cultos = []
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
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    try:
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cultos (
                id {id_tipo},
                data_culto TEXT,
                tipo_culto TEXT,
                homens_adultos INTEGER DEFAULT 0,
                mulheres_adultas INTEGER DEFAULT 0,
                jovens_rapazes INTEGER DEFAULT 0,
                jovens_mocas INTEGER DEFAULT 0,
                criancas_meninos INTEGER DEFAULT 0,
                criancas_meninas INTEGER DEFAULT 0,
                visitantes_homens INTEGER DEFAULT 0,
                visitantes_mulheres INTEGER DEFAULT 0,
                apelos INTEGER DEFAULT 0,
                total_presentes INTEGER DEFAULT 0,
                pregador TEXT,
                tema_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    fd = request.form
    def n(k):
        v = fd.get(k)
        if v not in (None, ''):
            try: return int(v)
            except: pass
        return 0

    from datetime import datetime
    data_culto = (fd.get('data_culto') or '').strip()
    if not data_culto or data_culto in ('mm/dd/yyyy', '---'):
        data_culto = datetime.now().strftime('%Y-%m-%d')

    tipo_culto = (fd.get('tipo_culto') or 'Domingo Manhã').strip()
    ha = n('homens_adultos')
    ma = n('mulheres_adultas')
    jr = n('jovens_rapazes')
    jm = n('jovens_mocas')
    cm = n('criancas_meninos')
    cf = n('criancas_meninas')
    vh = n('visitantes_homens')
    vm = n('visitantes_mulheres')
    apelos = n('apelos')

    # SOMA AUTOMÁTICA FEITA PELO PYTHON
    total = ha + ma + jr + jm + cm + cf + vh + vm

    pregador = (fd.get('pregador') or '---').strip()
    tema = (fd.get('tema_mensagem') or '').strip()

    is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO cultos 
             (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas, 
              criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, 
              apelos, total_presentes, pregador, tema_mensagem)
             VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e:
        print("[ERRO GRAVAR CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')

@app.route('/cultos/registar', methods=['POST'])
@app.route('/culto/novo', methods=['POST'])
def cultos_novo_seguro():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    # 1. Garantir que a tabela existe
    try:
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cultos (
                id {id_tipo},
                data_culto TEXT,
                tipo_culto TEXT,
                homens_adultos INTEGER DEFAULT 0,
                mulheres_adultas INTEGER DEFAULT 0,
                jovens_rapazes INTEGER DEFAULT 0,
                jovens_mocas INTEGER DEFAULT 0,
                criancas_meninos INTEGER DEFAULT 0,
                criancas_meninas INTEGER DEFAULT 0,
                visitantes_homens INTEGER DEFAULT 0,
                visitantes_mulheres INTEGER DEFAULT 0,
                apelos INTEGER DEFAULT 0,
                total_presentes INTEGER DEFAULT 0,
                pregador TEXT,
                tema_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    # 2. Extração segura (NUNCA usa [], sempre usa .get())
    fd = request.form

    def extrair_int(chaves):
        for k in chaves:
            v = fd.get(k)
            if v not in (None, ''):
                try: return int(v)
                except: pass
        return 0

    data_culto = (fd.get('data_culto') or fd.get('data') or '---').strip()
    tipo_culto = (fd.get('tipo_culto') or fd.get('tipo') or 'Domingo Manhã').strip()

    ha = extrair_int(['homens_adultos', 'homens'])
    ma = extrair_int(['mulheres_adultas', 'mulheres'])
    jr = extrair_int(['jovens_rapazes', 'rapazes'])
    jm = extrair_int(['jovens_mocas', 'mocas'])
    c_meninos = extrair_int(['criancas_meninos', 'meninos'])
    c_meninas = extrair_int(['criancas_meninas', 'meninas'])
    v_homens = extrair_int(['visitantes_homens', 'v_homens'])
    v_mulheres = extrair_int(['visitantes_mulheres', 'v_mulheres'])
    apelos = extrair_int(['apelos', 'decisoes'])

    # Soma de segurança calculada no backend
    soma_calculada = ha + ma + jr + jm + c_meninos + c_meninas + v_homens + v_mulheres
    total_form = extrair_int(['total_presentes', 'total'])
    total = total_form if total_form > 0 else soma_calculada

    pregador = (fd.get('pregador') or fd.get('pregador_palavra') or '---').strip()
    tema = (fd.get('tema_mensagem') or fd.get('tema') or '').strip()

    is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO cultos 
             (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas, 
              criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, 
              apelos, total_presentes, pregador, tema_mensagem)
             VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, c_meninos, c_meninas, v_homens, v_mulheres, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e_cult:
        print("[ERRO AO GRAVAR CULTO]:", e_cult)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')

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
         id SERIAL PRIMARY KEY,
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

@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    fd = request.form
    nome = (fd.get('nome') or fd.get('nome_completo') or fd.get('nome_convertido') or 'Sem Nome').strip()
    telefone = (fd.get('telefone') or fd.get('contato') or fd.get('contacto') or '').strip()
    bairro = (fd.get('bairro') or fd.get('residencia') or '').strip()
    data_decisao = (fd.get('data_decisao') or fd.get('data') or fd.get('data_conversao') or '').strip()
    quem_convidou = (fd.get('quem_convidou') or fd.get('convidado_por') or fd.get('discipulador') or '').strip()
    culto_origem = (fd.get('culto_origem') or fd.get('tipo_culto') or 'Geral').strip()

    from datetime import datetime
    if not data_decisao or data_decisao in ('mm/dd/yyyy', '---'):
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, 'Acompanhamento'))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Registado -> {nome}")
    except Exception as e:
        print("[ERRO AO GRAVAR CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')

@app.context_processor
def injetar_dados_tabelas():
    ctx = {'convertidos': [], 'cultos': []}
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        try:
            cur.execute("SELECT * FROM novos_convertidos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols = [c[0] for c in cur.description]
                ctx['convertidos'] = [dict(zip(cols, r)) for r in cur.fetchall()]
        except Exception: pass
        try:
            cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols_c = [c[0] for c in cur.description]
                ctx['cultos'] = [dict(zip(cols_c, r)) for r in cur.fetchall()]
        except Exception: pass
    except Exception: pass
    return ctx
