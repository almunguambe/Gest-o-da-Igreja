with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir a definição de init_db para ser totalmente compatível com PostgreSQL e SQLite
trecho_antigo_inicio = "def init_db():"
idx_init = code.find(trecho_antigo_inicio)

if idx_init != -1:
    # Localizar o final da função init_db (onde começa a próxima rota ou função)
    fim_init = code.find("\n@app.", idx_init)
    if fim_init == -1:
        fim_init = code.find("\ndef ", idx_init + 20)

    novo_init_db = '''def init_db():
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
        c.execute(\'\'\'CREATE TABLE IF NOT EXISTS igrejas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            localizacao TEXT,
            responsavel TEXT,
            contacto TEXT
        )\'\'\')
        conn.commit()
    except Exception as e:
        print(f"[ALERTA INIT_DB SQLITE] {e}")
    finally:
        c.close()
        conn.close()
'''

    if fim_init != -1:
        code = code[:idx_init] + novo_init_db.strip() + "\n\n" + code[fim_init:]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("✓ init_db() adaptado com sucesso para PostgreSQL e SQLite!")
    else:
        print("Não foi possível encontrar o final de init_db()")
else:
    print("init_db() não encontrado no app.py")