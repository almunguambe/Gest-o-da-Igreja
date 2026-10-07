with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

nova_funcao_migracao = '''
def garantir_colunas_membros():
    """Garante que todas as colunas necessárias existam na tabela membros"""
    todas_colunas = [
        ('data_nascimento', 'VARCHAR(50)'),
        ('genero', 'VARCHAR(20)'),
        ('estado_civil', 'VARCHAR(50)'),
        ('telefone', 'VARCHAR(50)'),
        ('email', 'VARCHAR(100)'),
        ('endereco', 'TEXT'),
        ('bairro', 'VARCHAR(100)'),
        ('cidade', 'VARCHAR(100)'),
        ('naturalidade', 'VARCHAR(100)'),
        ('profissao', 'VARCHAR(100)'),
        ('filiacao', 'VARCHAR(255)'),
        ('tipo_doc', 'VARCHAR(50)'),
        ('num_doc', 'VARCHAR(100)'),
        ('segmento', 'VARCHAR(50)'),
        ('ano_conversao', 'VARCHAR(50)'),
        ('data_conversao', 'VARCHAR(50)'),
        ('batizado', 'VARCHAR(20) DEFAULT "Não"'),
        ('data_batismo', 'VARCHAR(50)'),
        ('cargo', 'VARCHAR(100) DEFAULT "Membro em Comunhão"'),
        ('funcao', 'VARCHAR(100) DEFAULT "Membro"'),
        ('departamento', 'VARCHAR(100)'),
        ('status', 'VARCHAR(50) DEFAULT "Ativo"'),
        ('foto_path', 'VARCHAR(255)'),
        ('professor_id', 'INTEGER'),
        ('professor_nome', 'VARCHAR(150)')
    ]
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_postgres = bool(DATABASE_URL and psycopg2)
        
        if is_postgres:
            for col, tipo in todas_colunas:
                try:
                    cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
                    conn.commit()
                except Exception:
                    conn.rollback()
        else:
            cur.execute("PRAGMA table_info(membros);")
            existentes = [linha[1] for linha in cur.fetchall()]
            for col, tipo in todas_colunas:
                if col not in existentes:
                    try:
                        cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                        conn.commit()
                    except Exception:
                        pass
        if hasattr(conn, 'close'):
            conn.close()
        print("✓ Todas as colunas da tabela membros foram sincronizadas!")
    except Exception as e:
        print(f"! Aviso na migração: {e}")

try:
    garantir_colunas_membros()
except Exception:
    pass
'''

import re
if 'def garantir_colunas_membros():' in code:
    # Substitui a versão anterior pela lista completa
    padrao = r"def garantir_colunas_membros\(\):[\s\S]*?garantir_colunas_membros\(\)\s*except Exception:\s*pass"
    code = re.sub(padrao, nova_funcao_migracao.strip(), code)
else:
    code = code + "\n" + nova_funcao_migracao

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Script app.py atualizado com a migração universal de colunas!")