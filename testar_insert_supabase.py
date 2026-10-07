import os
import psycopg2
from app import DATABASE_URL, get_db

print("Conectando à base de dados...")
conn = get_db()
cur = conn.cursor() if hasattr(conn, 'cursor') else conn

campos = {
    'nome': 'Membro Teste Supabase',
    'telefone': '+258 84 000 0000',
    'igreja': 'IEAD Chicuque',
    'data_nascimento': '1995-01-01',
    'genero': 'Masculino',
    'estado_civil': 'Solteiro(a)',
    'bairro': 'Chicuque',
    'endereco': 'Chicuque Centro',
    'naturalidade': 'Maxixe',
    'filiacao': 'Pai Teste e Mãe Teste',
    'tipo_doc': 'BI',
    'num_doc': '080100000000A',
    'segmento': 'Jovens',
    'ano_conversao': '2020',
    'batizado': 'Sim',
    'cargo': 'Membro em Comunhão',
    'departamento': 'Geral',
    'status': 'Pendente de Validação',
    'foto_path': None,
    'professor_nome': 'Auto-recenseamento'
}

try:
    # 1. Inspecionar colunas na tabela membros
    cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'membros';")
    cols_info = cur.fetchall()
    print("\n--- COLUNAS ENCONTRADAS NA TABELA MEMBROS ---")
    for c in cols_info:
        print(f"Coluna: {c[0]} | Tipo: {c[1]} | Permite Nulo: {c[2]}")

    cols_db = [c[0].lower() for c in cols_info]
    cols_inserir = [k for k in campos.keys() if k.lower() in cols_db]
    vals_inserir = [campos[k] for k in cols_inserir]

    sql = f"INSERT INTO membros ({', '.join(cols_inserir)}) VALUES ({', '.join(['%s']*len(cols_inserir))}) RETURNING id;"
    print(f"\nTentando executar SQL:\n{sql}")
    
    cur.execute(sql, tuple(vals_inserir))
    novo_id = cur.fetchone()[0]
    conn.commit()
    print(f"\n✓ REGISTO INSERIDO COM SUCESSO! ID gerado: {novo_id}")

except Exception as erro:
    try:
        conn.rollback()
    except Exception:
        pass
    print(f"\n❌ ERRO DETETADO AO INSERIR NO POSTGRESQL:\n{erro}")

finally:
    if hasattr(conn, 'close'):
        conn.close()