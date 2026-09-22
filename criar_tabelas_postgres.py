import psycopg2

URL_DB = "postgresql://iead_chicuque_db_user:TwtchCgHGy1mLOSX96WWHnTlMUh6IZz5@dpg-damn06ad0e5s7382nksg-a.virginia-postgres.render.com/iead_chicuque_db"

print("Conectando à base de dados PostgreSQL na Virginia...")
try:
    conn = psycopg2.connect(URL_DB)
    cur = conn.cursor()
    print("Conexão estabelecida com sucesso! Criando tabelas...")

    # 1. Usuários
    cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(100) NOT NULL,
        cargo VARCHAR(100) NOT NULL
    )''')
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (%s, %s, %s)",
                    ('admin', 'chicuque123', 'Pastor Presidente'))

    # 2. Membros
    cur.execute('''CREATE TABLE IF NOT EXISTS membros (
        id SERIAL PRIMARY KEY,
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
    )''')

    # 3. Financeiro
    cur.execute('''CREATE TABLE IF NOT EXISTS financeiro (
        id SERIAL PRIMARY KEY,
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
    )''')

    # 4. Transferências
    cur.execute('''CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        data_movimento VARCHAR(20) NOT NULL,
        origem_local VARCHAR(50) NOT NULL,
        origem_depto VARCHAR(100) NOT NULL,
        destino_local VARCHAR(50) NOT NULL,
        destino_depto VARCHAR(100) NOT NULL,
        valor NUMERIC(12, 2) NOT NULL,
        motivo TEXT NOT NULL,
        data_registo VARCHAR(50) NOT NULL
    )''')

    # 5. Casamentos e Óbitos
    cur.execute('''CREATE TABLE IF NOT EXISTS casamentos (
        id SERIAL PRIMARY KEY,
        noivo VARCHAR(255) NOT NULL,
        noiva VARCHAR(255) NOT NULL,
        data_casamento VARCHAR(20) NOT NULL,
        pastor_oficiante VARCHAR(255),
        data_registo VARCHAR(20)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS mortes (
        id SERIAL PRIMARY KEY,
        nome_falecido VARCHAR(255) NOT NULL,
        data_falecimento VARCHAR(20) NOT NULL,
        observacoes TEXT,
        data_registo VARCHAR(20)
    )''')

    # 6. Listas Eclesiásticas
    cur.execute('''CREATE TABLE IF NOT EXISTS departamentos_lista (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) UNIQUE NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS categorias_financeiras (
        id SERIAL PRIMARY KEY,
        tipo VARCHAR(20) NOT NULL,
        nome VARCHAR(100) NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS zonas_lista (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) UNIQUE NOT NULL
    )''')

    # 7. Módulos Especiais
    cur.execute('''CREATE TABLE IF NOT EXISTS cultos_frequencia (
        id SERIAL PRIMARY KEY,
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
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS novos_convertidos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        telefone VARCHAR(50),
        bairro VARCHAR(100),
        data_decisao VARCHAR(20) NOT NULL,
        culto_origem VARCHAR(100),
        quem_convidou VARCHAR(255),
        status_discipulado VARCHAR(100) DEFAULT 'Decisão Inicial',
        observacoes TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS patrimonio (
        id SERIAL PRIMARY KEY,
        item VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Geral',
        quantidade INTEGER DEFAULT 1,
        estado_conservacao VARCHAR(50) DEFAULT 'Bom',
        localizacao VARCHAR(100),
        observacoes TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS escalas (
        id SERIAL PRIMARY KEY,
        data_escala VARCHAR(20) NOT NULL,
        tipo_culto VARCHAR(100) NOT NULL,
        dirigente VARCHAR(255),
        pregador VARCHAR(255),
        leitura_palavra VARCHAR(255),
        louvor_grupo VARCHAR(255),
        diaconos_servico VARCHAR(255),
        observacoes TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS campanhas_metas (
        id SERIAL PRIMARY KEY,
        nome_campanha VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) DEFAULT 'Construção',
        valor_meta NUMERIC(12, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'Ativa'
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS avaliacoes_estudantes (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(100) NOT NULL,
        licao VARCHAR(255) NOT NULL,
        nota INTEGER NOT NULL,
        total INTEGER NOT NULL,
        data_resposta VARCHAR(50) NOT NULL
    )''')

    # Departamentos Iniciais
    deptos = [
        ('Activista',), ('Juventude',), ('Mulher (Senhoras)',), 
        ('Boa Esperança (Crianças)',), ('Homens / Obreiros',), 
        ('Louvor / Música',), ('Ação Social',), ('Construção',)
    ]
    for d in deptos:
        cur.execute("INSERT INTO departamentos_lista (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING", d)

    cur.execute("SELECT COUNT(*) FROM categorias_financeiras")
    if cur.fetchone()[0] == 0:
        padroes = [
            ('Entrada', 'Dízimo'), ('Entrada', 'Oferta'), ('Entrada', 'Doação / Voto'), ('Entrada', 'Campanha de Construção'),
            ('Saída', 'Manutenção do Templo'), ('Saída', 'Ação Social / Ajudas'), ('Saída', 'Combustível / Transporte'),
            ('Saída', 'Água e Eletricidade'), ('Saída', 'Material de Culto')
        ]
        cur.executemany("INSERT INTO categorias_financeiras (tipo, nome) VALUES (%s, %s)", padroes)

    cur.execute("SELECT COUNT(*) FROM zonas_lista")
    if cur.fetchone()[0] == 0:
        zonas = [('Chicuque Sede',), ('Maxixe Cidade',), ('Nhacoongo',), ('Conguiana',), ('Bairro 1',)]
        cur.executemany("INSERT INTO zonas_lista (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING", zonas)

    cur.execute("SELECT COUNT(*) FROM campanhas_metas")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO campanhas_metas (nome_campanha, departamento, valor_meta, status) VALUES (%s, %s, %s, %s)",
                    ('Campanha de Obras e Ampliação do Templo', 'Construção', 100000.0, 'Ativa'))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Sucesso absoluto! Todas as tabelas foram criadas no PostgreSQL da Virginia!")

except Exception as e:
    print(f"Erro ao conectar ou criar tabelas: {e}")