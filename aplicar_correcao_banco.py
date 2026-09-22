import os

codigo_adaptador = '''import os
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

class DBWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        q = query
        if self.is_pg:
            # Converte marcadores ? para %s para PostgreSQL
            q = q.replace("?", "%s")
        try:
            if params:
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            print(f"Erro SQL ({q}): {e}")
            raise e
        return cur

def get_db():
    if IS_POSTGRES:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(RAW_DB_URL, cursor_factory=psycopg2.extras.DictCursor)
        return DBWrapper(conn, is_pg=True)
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return DBWrapper(conn, is_pg=False)

def init_db():
    db = get_db()
    pk_tipo = "SERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    # 1. Usuários
    db.execute(f"""CREATE TABLE IF NOT EXISTS usuarios (
        id {pk_tipo},
        usuario VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(100) NOT NULL,
        cargo VARCHAR(100) NOT NULL
    )""")
    db.commit()

    res = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()
    if res[0] == 0:
        db.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                   ('admin', 'chicuque123', 'Pastor Presidente'))
        db.commit()

    # 2. Membros
    db.execute(f"""CREATE TABLE IF NOT EXISTS membros (
        id {pk_tipo},
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
    db.commit()

    # 3. Financeiro
    db.execute(f"""CREATE TABLE IF NOT EXISTS financeiro (
        id {pk_tipo},
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
    db.commit()

    # 4. Transferências
    db.execute(f"""CREATE TABLE IF NOT EXISTS transferencias (
        id {pk_tipo},
        data_movimento VARCHAR(20) NOT NULL,
        origem_local VARCHAR(50) NOT NULL,
        origem_depto VARCHAR(100) NOT NULL,
        destino_local VARCHAR(50) NOT NULL,
        destino_depto VARCHAR(100) NOT NULL,
        valor NUMERIC(12, 2) NOT NULL,
        motivo TEXT NOT NULL,
        data_registo VARCHAR(50) NOT NULL
    )""")
    db.commit()

    # 5. Casamentos e Mortes
    db.execute(f"""CREATE TABLE IF NOT EXISTS casamentos (
        id {pk_tipo},
        noivo VARCHAR(255) NOT NULL,
        noiva VARCHAR(255) NOT NULL,
        data_casamento VARCHAR(20) NOT NULL,
        pastor_oficiante VARCHAR(255),
        data_registo VARCHAR(20)
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS mortes (
        id {pk_tipo},
        nome_falecido VARCHAR(255) NOT NULL,
        data_falecimento VARCHAR(20) NOT NULL,
        observacoes TEXT,
        data_registo VARCHAR(20)
    )""")
    db.commit()

    # 6. Listas Eclesiásticas
    db.execute(f"""CREATE TABLE IF NOT EXISTS departamentos_lista (
        id {pk_tipo},
        nome VARCHAR(100) UNIQUE NOT NULL
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS categorias_financeiras (
        id {pk_tipo},
        tipo VARCHAR(20) NOT NULL,
        nome VARCHAR(100) NOT NULL
    )""")
    db.execute(f"""CREATE TABLE IF NOT EXISTS zonas_lista (
        id {pk_tipo},
        nome VARCHAR(100) UNIQUE NOT NULL
    )""")
    db.commit()

    # 7. Módulos Especiais
    db.execute(f"""CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id {pk_tipo},
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
        id {pk_tipo},
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
        id {pk_tipo},
        item VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Geral',
        quantidade INTEGER DEFAULT 1,
        estado_conservacao VARCHAR(50) DEFAULT 'Bom',
        localizacao VARCHAR(100),
        observacoes TEXT
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS escalas (
        id {pk_tipo},
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
        id {pk_tipo},
        nome_campanha VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Construção',
        valor_meta NUMERIC(12, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'Ativa'
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
        id {pk_tipo},
        usuario VARCHAR(100) NOT NULL,
        licao VARCHAR(255) NOT NULL,
        nota INTEGER NOT NULL,
        total INTEGER NOT NULL,
        data_resposta VARCHAR(50) NOT NULL
    )""")

    db.execute(f"""CREATE TABLE IF NOT EXISTS duvidas_estudantes (
        id {pk_tipo},
        usuario VARCHAR(100) NOT NULL,
        licao VARCHAR(255) NOT NULL,
        duvida TEXT NOT NULL,
        resposta TEXT,
        data_envio VARCHAR(50) NOT NULL
    )""")
    db.commit()

    # Inserção de dados padrão de forma segura
    deptos = ['Activista', 'Juventude', 'Mulher (Senhoras)', 'Boa Esperança (Crianças)', 'Homens / Obreiros', 'Louvor / Música', 'Ação Social', 'Construção']
    for d in deptos:
        try:
            db.execute("INSERT INTO departamentos_lista (nome) VALUES (?)", (d,))
            db.commit()
        except:
            pass

    if db.execute("SELECT COUNT(*) FROM categorias_financeiras").fetchone()[0] == 0:
        padroes = [
            ('Entrada', 'Dízimo'), ('Entrada', 'Oferta'), ('Entrada', 'Doação / Voto'), ('Entrada', 'Campanha de Construção'),
            ('Saída', 'Manutenção do Templo'), ('Saída', 'Ação Social / Ajudas'), ('Saída', 'Combustível / Transporte'),
            ('Saída', 'Água e Eletricidade'), ('Saída', 'Material de Culto')
        ]
        for t, n in padroes:
            try:
                db.execute("INSERT INTO categorias_financeiras (tipo, nome) VALUES (?, ?)", (t, n))
                db.commit()
            except:
                pass

    zonas = ['Chicuque Sede', 'Maxixe Cidade', 'Nhacoongo', 'Conguiana', 'Bairro 1']
    for z in zonas:
        try:
            db.execute("INSERT INTO zonas_lista (nome) VALUES (?)", (z,))
            db.commit()
        except:
            pass

    if db.execute("SELECT COUNT(*) FROM campanhas_metas").fetchone()[0] == 0:
        try:
            db.execute("INSERT INTO campanhas_metas (nome_campanha, departamento, valor_meta, status) VALUES (?, ?, ?, ?)",
                       ('Campanha de Obras e Ampliação do Templo', 'Construção', 100000.0, 'Ativa'))
            db.commit()
        except:
            pass

    db.close()

try:
    init_db()
    print("✓ Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"Aviso na inicialização do banco: {e}")
'''

# Leitura do app.py atual para preservar todas as rotas
with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Localizar onde começam as funções auxiliares/rotas
indice_corte = 0
for i, linha in enumerate(linhas):
    if "def is_admin():" in linha:
        indice_corte = i
        break

if indice_corte > 0:
    resto_do_codigo = "".join(linhas[indice_corte:])
    codigo_final = codigo_adaptador + "\n" + resto_do_codigo
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(codigo_final)
    print("✓ app.py adaptado com motor híbrido SQLite + PostgreSQL!")
else:
    print("! Verifique o app.py manualmente: 'def is_admin():' não foi encontrado.")