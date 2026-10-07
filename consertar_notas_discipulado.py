with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Substituir a criação de tabela e o INSERT da avaliação para suportar PostgreSQL (%s) e SQLite (?)
trecho_antigo = """    # Gravar progresso de forma segura
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS progresso_discipulado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER,
                classe_id TEXT,
                nota REAL,
                status TEXT,
                data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")
        c.execute(\"\"\"
            INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
            VALUES (?, ?, ?, ?)
        \"\"\", (m_id, cid, nota_final, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso ao salvar progresso: {e}")"""

trecho_novo = """    # Gravar progresso de forma segura (Compatível com PostgreSQL e SQLite)
    try:
        conn = get_db_connection()
        c = conn.cursor()
        is_pg = bool(DATABASE_URL and psycopg2)

        if is_pg:
            c.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS progresso_discipulado (
                    id SERIAL PRIMARY KEY,
                    membro_id INTEGER,
                    classe_id TEXT,
                    nota REAL,
                    status TEXT,
                    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            \"\"\")
            # Atualiza se ja existir para essa classe, ou insere novo
            c.execute(\"\"\"
                DELETE FROM progresso_discipulado WHERE membro_id = %s AND classe_id = %s
            \"\"\", (m_id, cid))
            c.execute(\"\"\"
                INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
                VALUES (%s, %s, %s, %s)
            \"\"\", (m_id, cid, nota_final, status))
        else:
            c.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS progresso_discipulado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membro_id INTEGER,
                    classe_id TEXT,
                    nota REAL,
                    status TEXT,
                    data_conclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            \"\"\")
            c.execute(\"\"\"
                DELETE FROM progresso_discipulado WHERE membro_id = ? AND classe_id = ?
            \"\"\", (m_id, cid))
            c.execute(\"\"\"
                INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)
                VALUES (?, ?, ?, ?)
            \"\"\", (m_id, cid, nota_final, status))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar progresso do discipulado: {e}")"""

if "c.execute(\"\"\"\n            INSERT INTO progresso_discipulado (membro_id, classe_id, nota, status)\n            VALUES (?, ?, ?, ?)" in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("✓ Bloco de inserção do progresso_discipulado compatibilizado com PostgreSQL!")
else:
    # Se houver variação de identação, substitui via regex
    padrao = r"# Gravar progresso de forma segura.*?print\(f\"Aviso ao salvar progresso: \{e\}\"\)"
    conteudo = re.sub(padrao, trecho_novo, conteudo, flags=re.DOTALL)
    print("✓ Bloco de inserção atualizado via regex!")

# 2. Garantir que se m_id for inválido ou não informado, vincule ao primeiro membro ativo ou sessão
bloco_mid_antigo = """    classe = CURRICULO_CLASSES[cid]
    m_id = request.form.get('membro_id', 1)
    try:
        m_id = int(m_id)
    except:
        m_id = 1"""

bloco_mid_novo = """    classe = CURRICULO_CLASSES[cid]
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
        m_id = 1"""

if "classe = CURRICULO_CLASSES[cid]\n    m_id = request.form.get('membro_id', 1)" in conteudo:
    conteudo = conteudo.replace(bloco_mid_antigo, bloco_mid_novo)
    print("✓ Lógica de resolução segura do membro_id aplicada com sucesso!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)