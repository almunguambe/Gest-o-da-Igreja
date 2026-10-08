import os
import shutil
import ast
import re

print("=" * 65)
print("INICIANDO A CORREÇÃO DEFINITIVA PARA A APRESENTAÇÃO...")
print("=" * 65)

# 1. BACKUP
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
    print("✓ Backup criado: app.py.bak")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. FUNÇÃO QUE CRIA A TABELA NO BANCO LOGO NA INICIALIZAÇÃO
tabela_sql = '''
def criar_tabela_planificacoes_garantida():
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS planificacoes (
                id {id_tipo},
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
        if hasattr(conn, 'close'):
            conn.close()
    except Exception as e:
        print("[AVISO CRIACAO TABELA PLANIFICACOES]:", e)

try:
    criar_tabela_planificacoes_garantida()
except Exception:
    pass
'''

if "def criar_tabela_planificacoes_garantida" not in code:
    # Insere logo após a definição de get_db
    pos_get_db = code.find("def get_db():")
    if pos_get_db != -1:
        fim_get_db = code.find("\n\n", pos_get_db)
        code = code[:fim_get_db] + "\n\n" + tabela_sql.strip() + "\n" + code[fim_get_db:]
    else:
        code = tabela_sql.strip() + "\n\n" + code

# 3. ROTA COMPLETA E ROBUSTA DE GRAVAÇÃO E LEITURA
rota_correta = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS planificacoes (
                id {id_tipo},
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
        pass

    if request.method == 'POST':
        fd = request.form
        departamento = (fd.get('departamento') or 'Geral').strip()
        tipo_evento = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome_actividade = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data_prevista = (fd.get('data_prevista') or fd.get('data') or '').strip()
        frequencia = (fd.get('frequencia') or 'Pontual / Única').strip()
        responsavel = (fd.get('responsavel_directo') or fd.get('responsavel') or '').strip()
        contacto = (fd.get('contacto') or fd.get('telefone') or '').strip()

        marcador = "%s" if is_pg else "?"
        sql = f"""INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception as err:
            print("[ERRO GRAVACAO PLANIFICACAO]:", err)
            if hasattr(conn, 'rollback'):
                conn.rollback()
        finally:
            if hasattr(conn, 'close'):
                conn.close()

        ref = request.referrer
        if ref and '/secretaria/planificacao/nova' in ref:
            return redirect('/secretaria/planificacao/nova')
        return redirect(ref or '/secretaria/planificacao/nova')

    # GET: Leitura das planificações
    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, r)) for r in cur.fetchall()]
        else:
            planos = cur.fetchall()
    except Exception as err:
        print("[ERRO LEITURA PLANOS]:", err)
    finally:
        if hasattr(conn, 'close'):
            conn.close()

    for tpl in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', tpl)):
            return render_template(tpl, planificacoes=planos, planos=planos)
            
    return render_template('dashboard.html', planificacoes=planos, planos=planos)
'''

# Substitui a rota antiga pela rota correta
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(rota_correta.strip() + "\n\n")
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

code = "".join(novas_linhas)

# 4. CORRIGIR A LEITURA DO DASHBOARD (Garantir conexão dedicada e variáveis certas)
bloco_leitura_dashboard = """
    # Leitura Dedicada e Segura de Planificacoes
    planos = []
    try:
        conn_p = get_db()
        cur_p = conn_p.cursor() if hasattr(conn_p, 'cursor') else conn_p
        cur_p.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur_p.description:
            cols_p = [desc[0] for desc in cur_p.description]
            planos = [dict(zip(cols_p, r)) for r in cur_p.fetchall()]
        else:
            planos = cur_p.fetchall()
        if hasattr(conn_p, 'close'):
            conn_p.close()
    except Exception as err:
        print("[AVISO DASHBOARD PLANOS]:", err)
        planos = []
"""

# Substitui qualquer bloco antigo que tentava ler antes do return render_template('dashboard.html'
if "conn_p = get_db()" not in code:
    code = re.sub(
        r"(planos\s*=\s*\[\][\s\S]*?)(return render_template\('dashboard\.html')",
        bloco_leitura_dashboard.strip() + "\n\n    \\2",
        code,
        count=1
    )

# Garante que planificacoes=planos é passado para o dashboard.html
if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# 5. VALIDAÇÃO POR AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py 100% validado sem erros de sintaxe!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe evitado na linha {e.lineno}: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# 6. LIMPEZA DOS TEMPLATES HTML
pasta_tpl = 'templates'
if os.path.exists(pasta_tpl):
    for r, _, files in os.walk(pasta_tpl):
        for f in files:
            if f.endswith('.html'):
                caminho = os.path.join(r, f)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html = arq.read()

                orig = html
                # Aceita tanto planificacoes como planos
                html = html.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html = html.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')

                # Remove o onclick que causava o congelamento
                html = re.sub(r'onclick="[^"]*this\.form\.submit\(\)[^"]*"', '', html)
                html = re.sub(r'onclick="[^"]*this\.innerHTML[^"]*"', '', html)

                # Remove scripts AJAX injetados anteriormente que pudessem conflituar
                html = re.sub(r'<script>[\s\S]*?A gravar na Base de Dados[\s\S]*?</script>', '', html)
                html = re.sub(r'<script>[\s\S]*?A gravar\.\.\.[\s\S]*?</script>', '', html)

                if orig != html:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    print(f"✓ Template limpo e corrigido: {f}")

print("=" * 65)
print("✓ TUDO CONCLUÍDO E PRONTO COM SUCESSO!")
print("=" * 65)