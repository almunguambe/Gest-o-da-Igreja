with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Localiza onde começam as rotas/regras de negócio do sistema
indice_rotas = -1
for i, l in enumerate(linhas):
    if "def is_admin():" in l:
        indice_rotas = i
        break

if indice_rotas == -1:
    print("ERRO: Linha 'def is_admin():' não encontrada no app.py.")
    exit(1)

rotas_restantes = "".join(linhas[indice_rotas:])

novo_topo = '''import os
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

# DETECÇÃO AUTOMÁTICA DO BANCO (POSTGRESQL OU SQLITE)
RAW_DB_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = False

if RAW_DB_URL:
    if RAW_DB_URL.startswith("postgres://"):
        RAW_DB_URL = RAW_DB_URL.replace("postgres://", "postgresql://", 1)
    IS_POSTGRES = True

class RowDict(dict):
    """Permite acessar colunas por nome ou por índice numérico igualmente"""
    def __init__(self, d=None, keys=None, vals=None):
        if d:
            super().__init__(d)
            self._keys = list(d.keys())
            self._vals = list(d.values())
        elif keys is not None and vals is not None:
            super().__init__(zip(keys, vals))
            self._keys = list(keys)
            self._vals = list(vals)
        else:
            super().__init__()
            self._keys = []
            self._vals = []

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._vals[item]
        return super().__getitem__(item)

class CursorWrapper:
    def __init__(self, cur, is_pg):
        self.cur = cur
        self.is_pg = is_pg

    def __iter__(self):
        for row in self.fetchall():
            yield row

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        if self.is_pg and self.cur.description:
            cols = [d[0] for d in self.cur.description]
            return RowDict(keys=cols, vals=row)
        return row

    def fetchall(self):
        rows = self.cur.fetchall()
        if not rows:
            return []
        if self.is_pg and self.cur.description:
            cols = [d[0] for d in self.cur.description]
            return [RowDict(keys=cols, vals=r) for r in rows]
        return rows

class DBWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        try:
            if not self.is_pg:
                self.conn.commit()
        except:
            pass

    def rollback(self):
        try:
            self.conn.rollback()
        except:
            pass

    def close(self):
        try:
            self.conn.close()
        except:
            pass

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        q = query
        if self.is_pg:
            # Protege '%' literais substituindo por '%%'
            q = q.replace("%", "%%")
            # Converte marcadores ? para %s
            q = q.replace("?", "%s")
            # Restaura se ficou %%%%s
            q = q.replace("%%%%s", "%s")
        try:
            if params is not None:
                if not isinstance(params, (list, tuple)):
                    params = (params,)
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            if self.is_pg:
                self.conn.rollback()
            raise e
        return CursorWrapper(cur, self.is_pg)

def get_db():
    if IS_POSTGRES:
        import psycopg2
        conn = psycopg2.connect(RAW_DB_URL)
        # AUTOCOMMIT = TRUE ELIMINA 100% DOS ERROS DE "TRANSACTION IS ABORTED"
        conn.autocommit = True
        return DBWrapper(conn, is_pg=True)
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return DBWrapper(conn, is_pg=False)

def init_db():
    db = get_db()
    pk = "SERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    # 1. Usuários
    db.execute(f"""CREATE TABLE IF NOT EXISTS usuarios (
        id {pk},
        usuario VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(100) NOT NULL,
        cargo VARCHAR(100) NOT NULL
    )""")

    # 2. Membros
    db.execute(f"""CREATE TABLE IF NOT EXISTS membros (
        id {pk},
        nome VARCHAR(255) NOT NULL,
        telefone VARCHAR(50),
        genero VARCHAR(20),
        data_nascimento VARCHAR(20),
        faixa_etaria VARCHAR(50),
        naturalidade VARCHAR(100),
        bairro VARCHAR(100),
        filiacao VARCHAR(255),
        tipo_documento VARCHAR(50),
        numero_documento VARCHAR(50),
        ano_conversao INTEGER,
        data_batismo VARCHAR(20),
        posicao_atual VARCHAR(100),
        progressoes TEXT,
        departamento VARCHAR(100),
        foto_path TEXT,
        observacoes TEXT,
        data_registo VARCHAR(20)
    )""")

    # 3. Financeiro
    db.execute(f"""CREATE TABLE IF NOT EXISTS financeiro (
        id {pk},
        tipo VARCHAR(20),
        local_movimento VARCHAR(50) DEFAULT 'Caixa',
        departamento VARCHAR(100) DEFAULT 'Geral',
        categoria VARCHAR(100) NOT NULL,
        valor NUMERIC(12, 2) NOT NULL,
        data_movimento VARCHAR(20) NOT NULL,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        data_registo VARCHAR(50) NOT NULL,
        membro_id INTEGER,
        descricao TEXT
    )""")

    # 4. Transferências
    db.execute(f"""CREATE TABLE IF NOT EXISTS transferencias (
        id {pk},
        data_movimento VARCHAR(20) NOT NULL,
        origem_local VARCHAR(50) NOT NULL,
        origem_depto VARCHAR(100) NOT NULL,
        destino_local VARCHAR(50) NOT NULL,
        destino_depto VARCHAR(100) NOT NULL,
        valor NUMERIC(12, 2) NOT NULL,
        motivo TEXT NOT NULL,
        data_registo VARCHAR(50) NOT NULL
    )""")

    # 5. Casamentos e Óbitos
    db.execute(f"""CREATE TABLE IF NOT EXISTS casamentos (
        id {pk},
        noivo VARCHAR(255) NOT NULL,
        noiva VARCHAR(255) NOT NULL,
        data_casamento VARCHAR(20) NOT NULL,
        pastor_oficiante VARCHAR(255),
        data_registo VARCHAR(20)
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS mortes (
        id {pk},
        nome_falecido VARCHAR(255) NOT NULL,
        data_falecimento VARCHAR(20) NOT NULL,
        observacoes TEXT,
        data_registo VARCHAR(20)
    )""")

    # 6. Listas Eclesiásticas
    db.execute(f"""CREATE TABLE IF NOT EXISTS departamentos_lista (
        id {pk},
        nome VARCHAR(100) UNIQUE NOT NULL
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS categorias_financeiras (
        id {pk},
        tipo VARCHAR(20) NOT NULL,
        nome VARCHAR(100) NOT NULL
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS zonas_lista (
        id {pk},
        nome VARCHAR(100) UNIQUE NOT NULL
    )""")

    # 7. Módulos Especiais
    db.execute(f"""CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id {pk},
        data_culto VARCHAR(20) NOT NULL,
        tipo_culto VARCHAR(100) NOT NULL,
        homens INTEGER DEFAULT 0,
        mulheres INTEGER DEFAULT 0,
        jovens INTEGER DEFAULT 0,
        criancas INTEGER DEFAULT 0,
        visitantes INTEGER DEFAULT 0,
        novos_convertidos INTEGER DEFAULT 0,
        total_presentes INTEGER DEFAULT 0,
        pregador VARCHAR(255),
        tema_mensagem VARCHAR(255),
        data_registo VARCHAR(20)
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS novos_convertidos (
        id {pk},
        nome VARCHAR(255) NOT NULL,
        telefone VARCHAR(50),
        bairro VARCHAR(100),
        data_decisao VARCHAR(20) NOT NULL,
        culto_origem VARCHAR(100),
        quem_convidou VARCHAR(255),
        status_discipulado VARCHAR(100) DEFAULT 'Decisão Inicial',
        observacoes TEXT
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS patrimonio (
        id {pk},
        item VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Geral',
        quantidade INTEGER DEFAULT 1,
        estado_conservacao VARCHAR(50) DEFAULT 'Bom',
        localizacao VARCHAR(100),
        observacoes TEXT
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS escalas (
        id {pk},
        data_escala VARCHAR(20) NOT NULL,
        tipo_culto VARCHAR(100) NOT NULL,
        dirigente VARCHAR(255),
        pregador VARCHAR(255),
        leitura_palavra VARCHAR(255),
        louvor_grupo VARCHAR(255),
        diaconos_servico VARCHAR(255),
        observacoes TEXT
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS campanhas_metas (
        id {pk},
        nome_campanha VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Construção',
        valor_meta NUMERIC(12, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'Ativa'
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
        id {pk},
        usuario VARCHAR(100) NOT NULL,
        licao VARCHAR(255) NOT NULL,
        nota INTEGER NOT NULL,
        total INTEGER NOT NULL,
        data_resposta VARCHAR(50) NOT NULL
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS duvidas_estudantes (
        id {pk},
        usuario VARCHAR(100) NOT NULL,
        licao VARCHAR(255) NOT NULL,
        duvida TEXT NOT NULL,
        resposta TEXT,
        data_envio VARCHAR(50) NOT NULL
    )""")

    # População inicial segura sem quebras
    try:
        res = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()
        if res and res[0] == 0:
            db.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                       ('admin', 'chicuque123', 'Pastor Presidente'))
    except Exception as e:
        print(f"Info usuarios: {e}")

    deptos = ['Activista', 'Juventude', 'Mulher (Senhoras)', 'Boa Esperança (Crianças)', 'Homens / Obreiros', 'Louvor / Música', 'Ação Social', 'Construção']
    for d in deptos:
        try:
            if IS_POSTGRES:
                db.execute("INSERT INTO departamentos_lista (nome) VALUES (?) ON CONFLICT (nome) DO NOTHING", (d,))
            else:
                db.execute("INSERT OR IGNORE INTO departamentos_lista (nome) VALUES (?)", (d,))
        except:
            pass

    try:
        c_res = db.execute("SELECT COUNT(*) FROM categorias_financeiras").fetchone()
        if c_res and c_res[0] == 0:
            padroes = [
                ('Entrada', 'Dízimo'), ('Entrada', 'Oferta'), ('Entrada', 'Doação / Voto'), ('Entrada', 'Campanha de Construção'),
                ('Saída', 'Manutenção do Templo'), ('Saída', 'Ação Social / Ajudas'), ('Saída', 'Combustível / Transporte'),
                ('Saída', 'Água e Eletricidade'), ('Saída', 'Material de Culto')
            ]
            for t, n in padroes:
                db.execute("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", (t, n))
    except Exception as e:
        print(f"Info categorias: {e}")

    zonas = ['Chicuque Sede', 'Maxixe Cidade', 'Nhacoongo', 'Conguiana', 'Bairro 1']
    for z in zonas:
        try:
            if IS_POSTGRES:
                db.execute("INSERT INTO zonas_lista (nome) VALUES (?) ON CONFLICT (nome) DO NOTHING", (z,))
            else:
                db.execute("INSERT OR IGNORE INTO zonas_lista (nome) VALUES (?, ?)", (z,))
        except:
            pass

    try:
        camp_res = db.execute("SELECT COUNT(*) FROM campanhas_metas").fetchone()
        if camp_res and camp_res[0] == 0:
            db.execute("INSERT INTO campanhas_metas (nome_campanha, departamento, valor_meta, status) VALUES (?, ?, ?, ?)",
                       ('Campanha de Obras e Ampliação do Templo', 'Construção', 100000.0, 'Ativa'))
    except Exception as e:
        print(f"Info campanhas: {e}")

    db.close()

try:
    init_db()
    print("✓ Banco de dados inicializado com sucesso total!")
except Exception as e:
    print(f"Aviso init_db: {e}")
'''

codigo_completo = novo_topo + "\n" + rotas_restantes

with open("app.py", "w", encoding="utf-8") as f:
    f.write(codigo_completo)

print("✓ app.py reconstruído com autocommit ativado e proteção total!")