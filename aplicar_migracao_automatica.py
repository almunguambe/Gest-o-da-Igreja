with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Bloco de migração garantida para SQLite e PostgreSQL
codigo_migracao = '''
def garantir_colunas_membros():
    """Garante que todas as colunas da tabela membros existam no banco ativo"""
    colunas_necessarias = [
        ('endereco', 'TEXT'),
        ('bairro', 'VARCHAR(100)'),
        ('naturalidade', 'VARCHAR(100)'),
        ('filiacao', 'VARCHAR(255)'),
        ('tipo_doc', 'VARCHAR(50)'),
        ('num_doc', 'VARCHAR(100)'),
        ('segmento', 'VARCHAR(50)'),
        ('ano_conversao', 'VARCHAR(50)'),
        ('cargo', 'VARCHAR(100)'),
        ('professor_nome', 'VARCHAR(150)')
    ]
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_postgres = bool(DATABASE_URL and psycopg2)
        
        if is_postgres:
            for col, tipo in colunas_necessarias:
                try:
                    cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
                    conn.commit()
                except Exception:
                    conn.rollback()
        else:
            # SQLite
            cur.execute("PRAGMA table_info(membros);")
            existentes = [linha[1] for linha in cur.fetchall()]
            for col, tipo in colunas_necessarias:
                if col not in existentes:
                    try:
                        cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                        conn.commit()
                    except Exception:
                        pass
        if hasattr(conn, 'close'):
            conn.close()
        print("✓ Estrutura da tabela membros verificada e atualizada com sucesso!")
    except Exception as e:
        print(f"! Aviso na verificação de colunas: {e}")

# Executa ao iniciar o app
try:
    garantir_colunas_membros()
except Exception as e:
    pass
'''

if 'def garantir_colunas_membros():' not in code:
    # Insere logo após a definição do get_db() ou no final das conexões
    if 'def get_db():' in code:
        partes = code.split('def get_db():', 1)
        # Encontra o fim da função get_db aproximado ou adiciona antes das rotas
        code = code + "\n" + codigo_migracao
    else:
        code = code + "\n" + codigo_migracao
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Função garantir_colunas_membros() adicionada ao app.py com sucesso!")
else:
    print("Função de migração já existe no app.py.")