import sqlite3

conn = sqlite3.connect('gestao_chicuque.db')
cursor = conn.cursor()

# Adiciona as colunas caso ainda não existam
colunas_atuais = [c[1] for c in cursor.execute('PRAGMA table_info(escalas)').fetchall()]

if 'telefone_pregador' not in colunas_atuais:
    cursor.execute('ALTER TABLE escalas ADD COLUMN telefone_pregador TEXT DEFAULT ""')
    print("✓ Coluna telefone_pregador adicionada!")

if 'telefone_dirigente' not in colunas_atuais:
    cursor.execute('ALTER TABLE escalas ADD COLUMN telefone_dirigente TEXT DEFAULT ""')
    print("✓ Coluna telefone_dirigente adicionada!")

conn.commit()
conn.close()
print("✓ Base de dados pronta!")