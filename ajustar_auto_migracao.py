with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Função de migração segura embutida
migracao_code = '''
def executar_migracao_garantida():
    try:
        conn = get_db()
        c = conn.cursor()
        
        # 1. Tabela igrejas
        c.execute("""
            CREATE TABLE IF NOT EXISTS igrejas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                cidade TEXT,
                distrito TEXT,
                pastor TEXT,
                telefone TEXT,
                ativa INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("SELECT id FROM igrejas WHERE id = 1")
        if not c.fetchone():
            c.execute("""
                INSERT INTO igrejas (id, nome, cidade, distrito, pastor, telefone, ativa)
                VALUES (1, 'Congregação de Chicuque', 'Maxixe', 'Maxixe', 'Pastor Local', '+258 84 000 0000', 1)
            """)
        
        # 2. Adicionar igreja_id nas tabelas
        tabelas = [
            'usuarios', 'membros', 'financeiro', 'transferencias', 
            'casamentos', 'mortes', 'cultos_frequencia', 'novos_convertidos', 
            'patrimonio', 'escalas', 'campanhas_metas', 'zonas_lista', 
            'departamentos_lista', 'categorias_financeiras'
        ]
        for t in tabelas:
            try:
                c.execute(f"PRAGMA table_info({t})")
                colunas = [col[1] for col in c.fetchall()]
                if colunas and 'igreja_id' not in colunas:
                    c.execute(f"ALTER TABLE {t} ADD COLUMN igreja_id INTEGER DEFAULT 1")
            except Exception:
                pass
                
        # 3. Coluna is_superadmin em usuarios
        try:
            c.execute("PRAGMA table_info(usuarios)")
            cols_u = [col[1] for col in c.fetchall()]
            if 'is_superadmin' not in cols_u:
                c.execute("ALTER TABLE usuarios ADD COLUMN is_superadmin INTEGER DEFAULT 0")
            c.execute("UPDATE usuarios SET is_superadmin = 1, igreja_id = 1 WHERE usuario = 'admin'")
        except Exception:
            pass

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Aviso migracao inicial: {e}")

executar_migracao_garantida()
'''

if "def executar_migracao_garantida():" not in code:
    # Insere logo após a criação da app e get_db
    ponto = "def get_db():"
    idx = code.find(ponto)
    if idx != -1:
        fim_get_db = code.find("\n\n", idx)
        code = code[:fim_get_db] + "\n" + migracao_code + code[fim_get_db:]
        print("✓ Migração automática integrada com sucesso!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)