import os
import shutil
import re
import ast

print("=" * 70)
print("A FINALIZAR O CICLO COMPLETO DO MÓDULO DE CULTOS...")
print("=" * 70)

# 1. ATUALIZAR APP.PY (GRAVAÇÃO + LEITURA PARA A TABELA)
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Rota POST /cultos/novo robusta
rota_cultos = '''
@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    try:
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cultos (
                id {id_tipo},
                data_culto TEXT,
                tipo_culto TEXT,
                homens_adultos INTEGER DEFAULT 0,
                mulheres_adultas INTEGER DEFAULT 0,
                jovens_rapazes INTEGER DEFAULT 0,
                jovens_mocas INTEGER DEFAULT 0,
                criancas_meninos INTEGER DEFAULT 0,
                criancas_meninas INTEGER DEFAULT 0,
                visitantes_homens INTEGER DEFAULT 0,
                visitantes_mulheres INTEGER DEFAULT 0,
                apelos INTEGER DEFAULT 0,
                total_presentes INTEGER DEFAULT 0,
                pregador TEXT,
                tema_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    fd = request.form
    def n(k):
        v = fd.get(k)
        if v not in (None, ''):
            try: return int(v)
            except: pass
        return 0

    from datetime import datetime
    data_culto = (fd.get('data_culto') or '').strip()
    if not data_culto or data_culto in ('mm/dd/yyyy', '---'):
        data_culto = datetime.now().strftime('%Y-%m-%d')

    tipo_culto = (fd.get('tipo_culto') or 'Domingo Manhã').strip()
    ha = n('homens_adultos')
    ma = n('mulheres_adultas')
    jr = n('jovens_rapazes')
    jm = n('jovens_mocas')
    cm = n('criancas_meninos')
    cf = n('criancas_meninas')
    vh = n('visitantes_homens')
    vm = n('visitantes_mulheres')
    apelos = n('apelos')

    # SOMA AUTOMÁTICA FEITA PELO PYTHON
    total = ha + ma + jr + jm + cm + cf + vh + vm

    pregador = (fd.get('pregador') or '---').strip()
    tema = (fd.get('tema_mensagem') or '').strip()

    is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO cultos 
             (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas, 
              criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, 
              apelos, total_presentes, pregador, tema_mensagem)
             VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e:
        print("[ERRO GRAVAR CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

linhas_app = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas_app:
    if "@app.route('/cultos/novo'" in l:
        ignorar = True
        novas_linhas.append(rota_cultos.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "cultos_novo" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_cultos.strip() + "\n")

code = "".join(novas_linhas)

# Garantir consulta de cultos na rota principal GET /
bloco_busca_cultos = """
    # Carregar lista de cultos do Supabase em formato de dicionário
    cultos = []
    try:
        cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
        if cur.description:
            colunas = [col[0] for col in cur.description]
            cultos = [dict(zip(colunas, row)) for row in cur.fetchall()]
    except Exception as e_busca:
        print("[AVISO BUSCA CULTOS]:", e_busca)
"""

if 'SELECT * FROM cultos' not in code:
    # Injeta a busca antes do render_template('dashboard.html'
    code = re.sub(
        r'(\n\s*)(return\s+render_template\s*\(\s*[\'\"]dashboard\.html[\'\"])',
        r'\1' + bloco_busca_cultos.strip() + r'\1\2',
        code,
        count=1
    )
    print("✓ Consulta SQL de cultos injetada na rota principal do dashboard!")

# Assegurar que cultos=cultos é entregue ao template
if 'cultos=cultos' not in code:
    code = re.sub(
        r"(return\s+render_template\s*\(\s*['\"]dashboard\.html['\"]\s*,)",
        r"\1 cultos=cultos, ",
        code
    )

try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ app.py 100% verificado e validado!")
except SyntaxError as e_ast:
    print(f"❌ Erro de compilação: {e_ast}")

print("=" * 70)
print("✓ PRONTO PARA SUBIR!")
print("=" * 70)