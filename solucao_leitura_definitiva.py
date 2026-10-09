import os
import shutil
import ast

print("=" * 65)
print("A CORRIGIR A CONVERSÃO DOS DADOS DO SUPABASE PARA O ECRÃ...")
print("=" * 65)

# 1. BACKUP
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
    print("✓ Backup criado: app.py.bak")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. ROTA BLINDADA COM LEITURA UNIVERSAL DOS DADOS
rota_corrigida = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    # Limpeza preventiva da transação no PostgreSQL
    if hasattr(conn, 'rollback'):
        try: conn.rollback()
        except: pass

    # POST: GRAVAÇÃO DOS DADOS
    if request.method == 'POST':
        fd = request.form
        dep = (fd.get('departamento') or 'Geral').strip()
        tipo = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data = (fd.get('data_prevista') or fd.get('data') or '---').strip()
        freq = (fd.get('frequencia') or 'Pontual / Única').strip()
        resp = (fd.get('responsavel_directo') or fd.get('responsavel') or '---').strip()
        cont = (fd.get('contacto') or fd.get('telefone') or '').strip()

        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        marcador = "%s" if is_pg else "?"

        sql = f"""INSERT INTO planificacoes 
                 (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        try:
            cur.execute(sql, (dep, tipo, nome, data, freq, resp, cont))
            if hasattr(conn, 'commit'): conn.commit()
        except Exception as e_post:
            print("[ERRO AO GRAVAR PLANO]:", e_post)
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass

        return redirect('/secretaria/planificacao/nova')

    # GET: LEITURA COMPROVADA DO SUPABASE (Sem erros de tipo)
    planos = []
    try:
        cur.execute("SELECT id, departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status FROM planificacoes ORDER BY id DESC")
        linhas = cur.fetchall()
        for l in linhas:
            if hasattr(l, 'get'):
                item = {
                    'id': l.get('id'),
                    'departamento': l.get('departamento') or 'Geral',
                    'tipo_evento': l.get('tipo_evento') or 'Geral',
                    'nome_actividade': l.get('nome_actividade') or 'Actividade',
                    'data_prevista': l.get('data_prevista') or '---',
                    'frequencia': l.get('frequencia') or 'Pontual',
                    'responsavel_directo': l.get('responsavel_directo') or '---',
                    'contacto': l.get('contacto') or '',
                    'status': l.get('status') or 'Pendente'
                }
            else:
                item = {
                    'id': l[0],
                    'departamento': l[1] or 'Geral',
                    'tipo_evento': l[2] or 'Geral',
                    'nome_actividade': l[3] or 'Actividade',
                    'data_prevista': l[4] or '---',
                    'frequencia': l[5] or 'Pontual',
                    'responsavel_directo': l[6] or '---',
                    'contacto': l[7] or '',
                    'status': l[8] or 'Pendente'
                }
            planos.append(item)
        print(f"[DEBUG PLANIFICACOES] Registos encontrados no Supabase: {len(planos)}")
    except Exception as e_get:
        print("[ERRO AO LER PLANOS DO SUPABASE]:", e_get)

    # Identificar o template correto com o monitoramento do cronograma
    tpl_escolhido = 'nova_planificacao.html'
    pasta_tpl = 'templates'
    if os.path.exists(pasta_tpl):
        for f in os.listdir(pasta_tpl):
            if f.endswith('.html'):
                caminho = os.path.join(pasta_tpl, f)
                try:
                    with open(caminho, 'r', encoding='utf-8', errors='ignore') as arq:
                        if 'Monitoramento do Cronograma' in arq.read():
                            tpl_escolhido = f
                            break
                except:
                    pass

    return render_template(tpl_escolhido, planificacoes=planos, planos=planos)
'''

# 3. SUBSTITUIÇÃO SEGURA DA ROTA NO APP.PY
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(rota_corrigida.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_corrigida.strip() + "\n")

code_final = "".join(novas_linhas)

# 4. VALIDAÇÃO DE SINTAXE COM AST
try:
    ast.parse(code_final)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_final)
    print("✓ Backend app.py validado e corrigido sem erros de sintaxe!")
except SyntaxError as e:
    print(f"❌ Erro de compilação: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

print("=" * 65)
print("✓ OPERAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 65)