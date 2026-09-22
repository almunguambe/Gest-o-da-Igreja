with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garantir que a tabela membros tem zona, celula, bairro e distrito
bloco_migracao_colunas = '''
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
'''

if "def assegurar_colunas_geograficas():" not in conteudo:
    if "def get_db_connection():" in conteudo:
        partes = conteudo.split("def get_db_connection():")
        corpo = partes[1].split("\n@app.", 1)
        conteudo = partes[0] + "def get_db_connection():" + corpo[0] + "\n" + bloco_migracao_colunas + "\n@app." + corpo[1]

# 2. Atualizar a captura no cadastro de membros para incluir zona, celula, bairro e distrito
if "request.form.get('bairro'" in conteudo or "request.form.get('nome'" in conteudo:
    linhas = conteudo.splitlines()
    linhas_novas = []
    for l in linhas:
        linhas_novas.append(l)
        if "nome = request.form.get('nome'" in l or 'nome = request.form["nome"]' in l:
            linhas_novas.append("        zona = request.form.get('zona', '').strip()")
            linhas_novas.append("        celula = request.form.get('celula', '').strip()")
            linhas_novas.append("        distrito = request.form.get('distrito', '').strip()")

    conteudo = "\n".join(linhas_novas)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Colunas zona, celula, bairro e distrito migradas no app.py!")