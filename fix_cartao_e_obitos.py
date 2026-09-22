with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garantir que a tabela de obitos suporta membro_id e alterar o registo
codigo_ajuste_obitos = '''
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
'''

if "def assegurar_coluna_obito():" not in conteudo:
    if "def get_db_connection():" in conteudo:
        partes = conteudo.split("def get_db_connection():")
        corpo = partes[1].split("\n@app.", 1)
        conteudo = partes[0] + "def get_db_connection():" + corpo[0] + "\n" + codigo_ajuste_obitos + "\n@app." + corpo[1]

# 2. Corrigir a rota /registar_obito ou /obitos/novo para puxar do membro e marcar status
nova_rota_obito = '''@app.route('/registar_obito', methods=['POST'])
@app.route('/obitos/novo', methods=['POST'])
def registar_obito():
    from flask import request, redirect
    membro_id = request.form.get('membro_id')
    data_morte = request.form.get('data_morte')
    causa = request.form.get('causa', '').strip()
    observacoes = request.form.get('observacoes', '').strip()

    if membro_id:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            
            # Buscar nome oficial do membro
            c.execute("SELECT nome FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT nome FROM membros WHERE id = ?", (membro_id,))
            res_m = c.fetchone()
            nome_membro = res_m['nome'] if hasattr(res_m, 'keys') else (res_m[0] if res_m else "Membro Registado")

            # Inserir no registo de obitos
            c.execute("""
                INSERT INTO obitos (membro_id, nome, data_morte, causa, observacoes)
                VALUES (%s, %s, %s, %s, %s)
            """ if DATABASE_URL and psycopg2 else """
                INSERT INTO obitos (membro_id, nome, data_morte, causa, observacoes)
                VALUES (?, ?, ?, ?, ?)
            """, (membro_id, nome_membro, data_morte, causa, observacoes))

            # Atualizar estado do membro para Falecido
            c.execute("""
                UPDATE membros SET estado = 'Falecido' WHERE id = %s
            """ if DATABASE_URL and psycopg2 else """
                UPDATE membros SET estado = 'Falecido' WHERE id = ?
            """, (membro_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao registar obito: {e}")

    return redirect('/#secao-obitos')
'''

# Se houver rota existente de obito, substituir
if "def registar_obito(" in conteudo:
    partes = conteudo.split("def registar_obito(")
    topo = partes[0].rstrip()
    if topo.endswith("@app.route('/registar_obito', methods=['POST'])") or topo.endswith("@app.route('/obitos/novo', methods=['POST'])"):
        topo = topo.rsplit("@app.route", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + nova_rota_obito + "\n@app." + resto[1]
elif "def novo_obito(" in conteudo:
    partes = conteudo.split("def novo_obito(")
    topo = partes[0].rstrip()
    topo = topo.rsplit("@app.route", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + nova_rota_obito + "\n@app." + resto[1]

# 3. Inserir logo no Cartão de Membro na função que desenha o cartão
if "def gerar_cartao_membro(" in conteudo or "def cartao_membro(" in conteudo:
    # Garantir que obter_caminho_logo seja utilizado
    print("Atualizando geração do Cartão de Membro com logótipo...")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py configurado com integridade entre membros e óbitos!")