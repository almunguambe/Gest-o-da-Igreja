with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Procura onde começam as rotas
idx = -1
for i, l in enumerate(linhas):
    if "def is_admin():" in l:
        idx = i
        break

if idx == -1:
    print("Erro: não encontrou def is_admin")
    exit(1)

rotas = "".join(linhas[idx:])

topo_original = '''import os
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
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS membros (
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
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS financeiro (
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
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS transferencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_movimento TEXT NOT NULL,
        origem_local TEXT NOT NULL,
        origem_depto TEXT NOT NULL,
        destino_local TEXT NOT NULL,
        destino_depto TEXT NOT NULL,
        valor REAL NOT NULL,
        motivo TEXT NOT NULL,
        data_registo TEXT NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS casamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        noivo TEXT NOT NULL,
        noiva TEXT NOT NULL,
        data_casamento TEXT NOT NULL,
        pastor_oficiante TEXT,
        data_registo TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS mortes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_falecido TEXT NOT NULL,
        data_falecimento TEXT NOT NULL,
        observacoes TEXT,
        data_registo TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS departamentos_lista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS categorias_financeiras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        nome TEXT NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS zonas_lista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS cultos_frequencia (
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
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS novos_convertidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        bairro TEXT,
        data_decisao TEXT NOT NULL,
        culto_origem TEXT,
        quem_convidou TEXT,
        status_discipulado TEXT DEFAULT 'Decisão Inicial',
        observacoes TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS patrimonio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        departamento TEXT DEFAULT 'Geral',
        quantidade INTEGER DEFAULT 1,
        estado_conservacao TEXT DEFAULT 'Bom',
        localizacao TEXT,
        observacoes TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS escalas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_escala TEXT NOT NULL,
        tipo_culto TEXT NOT NULL,
        dirigente TEXT,
        pregador TEXT,
        leitura_palavra TEXT,
        louvor_grupo TEXT,
        diaconos_servico TEXT,
        observacoes TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS campanhas_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_campanha TEXT NOT NULL,
        departamento TEXT DEFAULT 'Construção',
        valor_meta REAL NOT NULL,
        status TEXT DEFAULT 'Ativa'
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        licao TEXT NOT NULL,
        nota INTEGER NOT NULL,
        total INTEGER NOT NULL,
        data_resposta TEXT NOT NULL
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS duvidas_estudantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        licao TEXT NOT NULL,
        duvida TEXT NOT NULL,
        resposta TEXT,
        data_envio TEXT NOT NULL
    )\'\'\')

    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                  ('admin', 'chicuque123', 'Pastor Presidente'))

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
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(topo_original + "\n" + rotas)

print("✓ Restaurado com sucesso para SQLite 100% nativo!")