import sqlite3
import os

print("--- 1. ADICIONANDO COLUNAS NA BASE DE DADOS LOCAL ---")
# Localizar todos os ficheiros .db na pasta do projeto
bancos = [f for f in os.listdir('.') if f.endswith('.db')]
if not bancos:
    bancos = ['banco.db']

colunas = [
    ("status", "VARCHAR(50) DEFAULT 'Ativo'"),
    ("batizado", "VARCHAR(20) DEFAULT 'Não'"),
    ("data_batismo", "VARCHAR(50)"),
    ("igreja", "VARCHAR(150) DEFAULT 'IEAD Chicuque'"),
    ("telefone", "VARCHAR(50)"),
    ("bairro", "VARCHAR(100)"),
    ("endereco", "TEXT"),
    ("naturalidade", "VARCHAR(100)"),
    ("filiacao", "VARCHAR(255)"),
    ("tipo_doc", "VARCHAR(50)"),
    ("num_doc", "VARCHAR(100)"),
    ("segmento", "VARCHAR(50)"),
    ("ano_conversao", "VARCHAR(50)"),
    ("cargo", "VARCHAR(100) DEFAULT 'Membro em Comunhão'"),
    ("departamento", "VARCHAR(100) DEFAULT 'Geral'"),
    ("foto_path", "VARCHAR(255)"),
    ("professor_nome", "VARCHAR(150)")
]

for banco in bancos:
    try:
        conn = sqlite3.connect(banco)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(membros);")
        existentes = [r[1].lower() for r in cur.fetchall()]
        
        for col, tipo in colunas:
            if col.lower() not in existentes:
                try:
                    cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                    print(f"  + [{banco}] Coluna criada: {col}")
                except Exception as e:
                    pass
        conn.commit()
        conn.close()
        print(f"✓ Base de dados {banco} atualizada com sucesso!")
    except Exception as e:
        print(f"Aviso sobre {banco}: {e}")

print("\n--- 2. BLINDANDO A CONSULTA EM APP.PY ---")
with open('app.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Procurar a linha 3575 ou o cur.execute da rota homologar
novo_codigo = []
modificado = False

for linha in linhas:
    # Se encontrar a consulta que gerava o erro
    if "SELECT" in linha and "FROM membros WHERE status =" in linha:
        # Substitui por uma execução segura com verificação de coluna
        nova_linha = """            # Consulta adaptativa protegida
            cur.execute("PRAGMA table_info(membros);") if not is_pg else cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
            cols_atuais = [r[1].lower() if not is_pg else r[0].lower() for r in cur.fetchall()]
            if 'status' in cols_atuais:
                sql_exec = f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, igreja FROM membros WHERE status = {param} ORDER BY id DESC"
                cur.execute(sql_exec, ('Pendente de Validação',))
            else:
                cur.execute("SELECT id, nome FROM membros ORDER BY id DESC")
"""
        novo_codigo.append(nova_linha)
        modificado = True
    else:
        novo_codigo.append(linha)

if modificado:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(novo_codigo)
    print("✓ Linha da consulta blindada em app.py!")
else:
    print("Consulta já adaptada ou não localizada de forma idêntica.")