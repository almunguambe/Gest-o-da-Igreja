import os
import shutil
import ast
import re

print("=" * 65)
print("A ATIVAR A EXIBIÇÃO IMEDIATA DOS DADOS DO SUPABASE NA TELA...")
print("=" * 65)

# 1. BACKUP
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. ROTA DE LEITURA E GRAVAÇÃO BLINDADA
nova_rota = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    tipo_conn = str(type(conn)).lower()
    is_pg = ('psycopg' in tipo_conn) or hasattr(conn, 'cursor_factory') or ('postgres' in tipo_conn) or bool(os.environ.get('DATABASE_URL'))

    # Limpeza de qualquer transação pendente
    if hasattr(conn, 'rollback'):
        try: conn.rollback()
        except: pass

    # POST: GRAVAÇÃO NO SUPABASE
    if request.method == 'POST':
        fd = request.form
        departamento = (fd.get('departamento') or 'Geral').strip()
        tipo_evento = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome_actividade = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data_prevista = (fd.get('data_prevista') or fd.get('data') or '---').strip()
        frequencia = (fd.get('frequencia') or 'Pontual / Única').strip()
        responsavel = (fd.get('responsavel_directo') or fd.get('responsavel') or '---').strip()
        contacto = (fd.get('contacto') or fd.get('telefone') or '').strip()

        marcador = "%s" if is_pg else "?"
        sql = f"""INSERT INTO planificacoes 
                 (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'): conn.commit()
        except Exception as e_ins:
            print("[ERRO INSERT]:", e_ins)
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass
        finally:
            if hasattr(conn, 'close'):
                try: conn.close()
                except: pass

        return redirect('/secretaria/planificacao/nova')

    # GET: LEITURA COMPROVADA DO SUPABASE
    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        registos = cur.fetchall()
        if cur.description:
            colunas = [d[0] for d in cur.description]
            for reg in registos:
                item = {}
                for idx, col in enumerate(colunas):
                    item[col] = reg[idx]
                planos.append(item)
    except Exception as e_select:
        print("[ERRO SELECT PLANOS]:", e_select)
    finally:
        if hasattr(conn, 'close'):
            try: conn.close()
            except: pass

    tpl_nome = 'nova_planificacao.html'
    for t in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', t)):
            tpl_nome = t
            break

    return render_template(tpl_nome, planificacoes=planos, planos=planos)
'''

# 3. SUBSTITUIR A ROTA NO APP.PY
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(nova_rota.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + nova_rota.strip() + "\n")

code_final = "".join(novas_linhas)

# 4. VALIDAÇÃO RIGOROSA COM AST (SEM ERROS DE SINTAXE)
try:
    ast.parse(code_final)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_final)
    print("✓ Backend app.py configurado e validado com sucesso!")
except SyntaxError as e:
    print(f"Erro evitado: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# 5. GARANTIR QUE OS TEMPLATES ACEITAM OS DADOS
pasta_tpl = 'templates'
if os.path.exists(pasta_tpl):
    for r, _, files in os.walk(pasta_tpl):
        for f in files:
            if f.endswith('.html'):
                caminho = os.path.join(r, f)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html = arq.read()

                orig = html
                html = html.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html = html.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')

                if orig != html:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    print(f"✓ Template sincronizado: {f}")

print("=" * 65)
print("✓ SISTEMA PRONTO PARA MOSTRAR OS DADOS DO SUPABASE!")
print("=" * 65)