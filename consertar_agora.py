import os
import shutil
import ast
import re

print("=" * 65)
print("A APLICAR A CORREÇÃO DEFINITIVA NO SISTEMA...")
print("=" * 65)

# 1. BACKUP
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. FUNÇÃO QUE CRIA A TABELA CORRETA NO BANCO
funcao_banco = '''
def assegurar_tabela_planificacoes(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_col = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS planificacoes (
                id {id_col},
                departamento TEXT,
                tipo_evento TEXT,
                nome_actividade TEXT,
                data_prevista TEXT,
                frequencia TEXT,
                responsavel_directo TEXT,
                contacto TEXT,
                status TEXT DEFAULT 'Pendente'
            );
        """)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception:
        try:
            if hasattr(conn, 'rollback'): conn.rollback()
        except Exception: pass
'''

if "def assegurar_tabela_planificacoes" not in code:
    code = funcao_banco.strip() + "\n\n" + code

# 3. CORRIGIR A LEITURA NO DASHBOARD (LER DE PLANIFICACOES)
bloco_leitura_correto = """assegurar_tabela_planificacoes(conn)
    planos = []
    try:
        cur_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_pl.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur_pl.description:
            cols_pl = [desc[0] for desc in cur_pl.description]
            planos = [dict(zip(cols_pl, r)) for r in cur_pl.fetchall()]
        else:
            planos = cur_pl.fetchall()
    except Exception:
        planos = []"""

# Substitui qualquer consulta à tabela antiga actividades_planeamento
code = re.sub(
    r"planos\s*=\s*conn\.execute\([\"']SELECT \* FROM actividades_planeamento.*?\)[\s\S]*?except Exception:\s*planos = \[\]",
    bloco_leitura_correto,
    code
)

# Garante que o dashboard entrega planificacoes=planos ao template
if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# 4. ROTA DE GRAVAÇÃO LIMPA (Sem bloqueios, com redirect imediato)
rota_limpa = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    assegurar_tabela_planificacoes(conn)
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    if request.method == 'POST':
        fd = request.form
        departamento = (fd.get('departamento') or 'Geral').strip()
        tipo_evento = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome_actividade = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data_prevista = (fd.get('data_prevista') or fd.get('data') or '').strip()
        frequencia = (fd.get('frequencia') or 'Pontual / Única').strip()
        responsavel = (fd.get('responsavel_directo') or fd.get('responsavel') or '').strip()
        contacto = (fd.get('contacto') or fd.get('telefone') or '').strip()

        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        marcador = "%s" if is_pg else "?"

        sql = f"""INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception as e:
            print("[ERRO AO GRAVAR PLANO]:", e)
            try:
                if hasattr(conn, 'rollback'): conn.rollback()
            except Exception: pass

        return redirect(request.referrer or '/')

    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, r)) for r in cur.fetchall()]
        else:
            planos = cur.fetchall()
    except Exception:
        planos = []

    for tpl in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', tpl)):
            return render_template(tpl, planificacoes=planos, planos=planos)

    return render_template('dashboard.html', planificacoes=planos, planos=planos)
'''

# Substitui com precisão a rota
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(rota_limpa.strip() + "\n\n")
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

code = "".join(novas_linhas)

# Validação com AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py validado e corrigido!")
except SyntaxError as e:
    print(f"Erro de sintaxe evitado: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# 5. LIMPAR OS TEMPLATES HTML (Descongelar o botão e aceitar ambas as variáveis)
pasta_t = 'templates'
if os.path.exists(pasta_t):
    for r, _, files in os.walk(pasta_t):
        for f in files:
            if f.endswith('.html'):
                caminho = os.path.join(r, f)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html = arq.read()

                orig = html
                # Aceita tanto 'planificacoes' como 'planos'
                html = html.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html = html.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')

                # Remove o onclick que causava o congelamento do botão
                html = re.sub(r'onclick="[^"]*this\.form\.submit\(\)[^"]*"', '', html)
                html = re.sub(r'onclick="[^"]*this\.innerHTML[^"]*"', '', html)

                # Remove scripts AJAX injetados anteriormente que pudessem conflituar
                html = re.sub(r'<script>[\s\S]*?A gravar na Base de Dados[\s\S]*?</script>', '', html)
                html = re.sub(r'<script>[\s\S]*?A gravar\.\.\.[\s\S]*?</script>', '', html)

                if orig != html:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    print(f"✓ Template limpo e sincronizado: {f}")

print("=" * 65)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
print("=" * 65)