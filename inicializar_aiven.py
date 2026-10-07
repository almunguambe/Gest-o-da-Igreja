import psycopg2

URL = "postgres://avnadmin:AVNS_d0xsHm5H0SjbbFNW-V8@pg-3d896ab-iead-chicuque-db.a.aivencloud.com:27231/defaultdb?sslmode=require"

print("Conectando ao banco Aiven...")
conn = psycopg2.connect(URL)
c = conn.cursor()

# 1. Tabela Financeiro
c.execute("""
CREATE TABLE IF NOT EXISTS financeiro (
    id SERIAL PRIMARY KEY,
    tipo TEXT,
    local_movimento TEXT DEFAULT 'Caixa',
    departamento TEXT DEFAULT 'Geral',
    categoria TEXT NOT NULL,
    valor NUMERIC NOT NULL,
    data_movimento TEXT NOT NULL,
    dia INTEGER,
    mes INTEGER,
    ano INTEGER,
    data_registo TEXT NOT NULL,
    membro_id INTEGER,
    descricao TEXT,
    metodo_pagamento TEXT DEFAULT 'Dinheiro',
    referencia_transacao TEXT
);
""")

# 2. Tabela Transferencias
c.execute("""
CREATE TABLE IF NOT EXISTS transferencias (
    id SERIAL PRIMARY KEY,
    data_movimento TEXT NOT NULL,
    origem_local TEXT NOT NULL,
    origem_depto TEXT NOT NULL,
    destino_local TEXT NOT NULL,
    destino_depto TEXT NOT NULL,
    valor NUMERIC NOT NULL,
    motivo TEXT,
    data_registo TEXT NOT NULL
);
""")

# 3. Tabela Membros
c.execute("""
CREATE TABLE IF NOT EXISTS membros (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    data_nascimento TEXT,
    genero TEXT,
    estado_civil TEXT,
    telefone TEXT,
    bairro TEXT,
    status_espiritual TEXT,
    classe_escola_dominical TEXT,
    departamento TEXT,
    cargo_lideranca TEXT,
    data_batismo TEXT,
    foto TEXT,
    data_cadastro TEXT
);
""")

# 4. Tabela Progresso Discipulado
c.execute("""
CREATE TABLE IF NOT EXISTS progresso_discipulado (
    id SERIAL PRIMARY KEY,
    membro_id INTEGER,
    classe_id TEXT,
    nota NUMERIC,
    status TEXT,
    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 5. Tabela Duvidas Discipulado
c.execute("""
CREATE TABLE IF NOT EXISTS duvidas_discipulado (
    id SERIAL PRIMARY KEY,
    membro_id INTEGER,
    classe_id TEXT,
    licao_id INTEGER,
    duvida TEXT,
    resposta TEXT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resposta TIMESTAMP
);
""")

# 6. Tabela Igrejas
c.execute("""
CREATE TABLE IF NOT EXISTS igrejas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    cidade TEXT,
    distrito TEXT,
    pastor TEXT,
    telefone TEXT,
    ativa INTEGER DEFAULT 1
);
""")

# 7. Tabela Casamentos
c.execute("""
CREATE TABLE IF NOT EXISTS casamentos (
    id SERIAL PRIMARY KEY,
    noivo TEXT NOT NULL,
    noiva TEXT NOT NULL,
    data_casamento TEXT NOT NULL,
    pastor_oficiante TEXT,
    data_registo TEXT NOT NULL
);
""")

conn.commit()
conn.close()
print("✓ Todas as tabelas essenciais criadas com sucesso no Aiven PostgreSQL!")