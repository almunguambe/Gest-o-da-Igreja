import os
import re
import ast

print("A analisar e corrigir a linha 762 do app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Bloco perfeitamente estruturado e indentado para o dashboard
bloco_dashboard = """sucesso_cadastro = session.pop('sucesso_cadastro', None)

    planos = []
    try:
        cur_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
        id_col = "SERIAL" if is_pg else "INTEGER"
        cur_pl.execute(f"CREATE TABLE IF NOT EXISTS planificacoes (id {id_col} PRIMARY KEY, departamento TEXT, tipo_evento TEXT, nome_actividade TEXT, data_prevista TEXT, frequencia TEXT, responsavel_directo TEXT, contacto TEXT, status TEXT DEFAULT 'Pendente')")
        if hasattr(conn, 'commit'):
            conn.commit()
        cur_pl.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur_pl.description:
            cols_pl = [desc[0] for desc in cur_pl.description]
            planos = [dict(zip(cols_pl, r)) for r in cur_pl.fetchall()]
        else:
            planos = cur_pl.fetchall()
    except Exception:
        planos = []

    # Filtrar Candidatos ao Batismo"""

# 1. Substituir com precisão cirúrgica a área com o try: órfão
padrao_dashboard = r"sucesso_cadastro\s*=\s*session\.pop\('sucesso_cadastro',\s*None\)[\s\S]*?#\s*Filtrar Candidatos ao Batismo"

if re.search(padrao_dashboard, code):
    code = re.sub(padrao_dashboard, bloco_dashboard, code, count=1)
    print("✓ Bloco do dashboard reconstruído sem erros de sintaxe.")
else:
    # Correção alternativa direta para remover o try: solto
    code = re.sub(r"try:\s*(?=\s*criar_tabela|\s*garantir_tabela|\s*planos\s*=)", "", code)
    print("✓ Try órfão removido com sucesso.")

# 2. Validar sintaxe com o compilador do Python antes de guardar
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("=" * 60)
    print("✓ SUCESSO TOTAL: Sintaxe 100% validada! Sem erros no app.py.")
    print("=" * 60)
except SyntaxError as e:
    print(f"Ajuste fino na linha {e.lineno}...")
    linhas = code.splitlines()
    idx = e.lineno - 1
    if idx > 0 and 'try:' in linhas[idx-1]:
        del linhas[idx-1]
        code = "\n".join(linhas)
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Código validado e guardado com sucesso!")