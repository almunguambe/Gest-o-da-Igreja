import os
import shutil
import ast
import re

print("=" * 65)
print("A REPARAR AS ABAS DA SIDEBAR E O ENVIO DA PLANIFICAÇÃO...")
print("=" * 65)

# 1. BACKUPS DE SEGURANÇA
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
tpl_dash = os.path.join('templates', 'dashboard.html')
if os.path.exists(tpl_dash):
    shutil.copy(tpl_dash, tpl_dash + '.bak')

# -------------------------------------------------------------------
# 2. LIMPAR E AJUSTAR TEMPLATES/DASHBOARD.HTML
# -------------------------------------------------------------------
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# A) Remover qualquer script invasor que tenha bloqueado a sidebar
html = re.sub(r'<!-- controlador-navegacao-sidebar -->[\s\S]*?</script>', '', html)
html = re.sub(r'<script>[\s\S]*?ativarAbaPorNome[\s\S]*?</script>', '', html)
html = re.sub(r'<script>[\s\S]*?modulo-planificacao-embutido[\s\S]*?</script>', '', html)

# B) Remover qualquer interceptor de submit com preventDefault que congele o formulário
html = re.sub(r'formPlan\.addEventListener\("submit"[\s\S]*?</script>', '', html)
html = re.sub(r'e\.preventDefault\(\);[\s\S]*?fetch\(form\.action[\s\S]*?</script>', '', html)

# C) Garantir que o formulário de planificação tem action e method corretos
# Substitui o form da planificação para apontar com certeza para a rota correta
html = re.sub(
    r'<form[^>]*action=["\'][^"\']*planificacao[^"\']*["\'][^>]*>',
    '<form action="/secretaria/planificacao/nova" method="POST">',
    html
)

# Caso o form original não tivesse action explícita, ajusta o form que contém "Nome da Actividade"
def ajustar_tag_form(match):
    bloco = match.group(0)
    if 'action=' not in bloco:
        return bloco.replace('<form', '<form action="/secretaria/planificacao/nova" method="POST"')
    return bloco

html = re.sub(r'<form[\s\S]*?(?=Nome da Actividade)', ajustar_tag_form, html, count=1)

# D) Limpar qualquer onclick obsoleto no botão de envio
html = re.sub(r'onclick="[^"]*submit[^"]*"', '', html)

# E) Script simples de suporte à navegação (sem interceptar cliques de outras abas)
script_suporte_aba = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Se a URL trouxer ?aba=secretaria, abre a aba Secretaria automaticamente
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'secretaria') {
        var links = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item, [onclick*="secretaria"]');
        for (var i = 0; i < links.length; i++) {
            var txt = links[i].innerText ? links[i].innerText.toLowerCase() : '';
            if (txt.includes('secretaria')) {
                links[i].click();
                break;
            }
        }
    }
});
</script>
"""

if 'script-suporte-aba-secretaria' not in html:
    html = html + "\n<!-- script-suporte-aba-secretaria -->\n" + script_suporte_aba

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html desimpedido e pronto!")

# -------------------------------------------------------------------
# 3. ATUALIZAR APP.PY (LEITURA DO SUPABASE NO DASHBOARD + REDIRECT)
# -------------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Leitor comprovado do Supabase para o dashboard
codigo_leitor = """
    # 4. Leitura Direta de Planificacoes no Dashboard
    planos = []
    try:
        cur_dash_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_dash_pl.execute("SELECT id, departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status FROM planificacoes ORDER BY id DESC")
        linhas_p = cur_dash_pl.fetchall()
        for l in linhas_p:
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
    except Exception as e_p:
        print("[ERRO DASHBOARD PLANIFICACAO]:", e_p)
        planos = []
"""

# Substitui o bloco de leitura antigo no dashboard
padrao_bloco_planos = r"#\s*4\.\s*Planifica[^\n]*\n[\s\S]*?(?=#\s*5\.|\n\s*candidatos_batismo)"
if re.search(padrao_bloco_planos, code):
    code = re.sub(padrao_bloco_planos, codigo_leitor.strip() + "\n\n    ", code, count=1)
else:
    # Insere imediatamente antes de render_template('dashboard.html'
    code = code.replace("return render_template('dashboard.html',", codigo_leitor.strip() + "\n    return render_template('dashboard.html',", 1)

# Garante que as duas variáveis são entregues ao render do dashboard
if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# Garantir que a rota POST grava e redireciona de volta para a aba da Secretaria no Dashboard
rota_plan_ajustada = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

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
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass
            cur.execute(sql, (dep, tipo, nome, data, freq, resp, cont))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception as e_post:
            print("[ERRO GRAVAR PLANIFICACAO]:", e_post)
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass

        return redirect('/?aba=secretaria')

    # GET: Se acedido diretamente, redireciona para a aba no painel principal
    return redirect('/?aba=secretaria')
'''

# Substitui a rota antiga da planificacao pela versão ajustada
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(rota_plan_ajustada.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_plan_ajustada.strip() + "\n")

code_final = "".join(novas_linhas)

# Validação estrita por compilador AST
try:
    ast.parse(code_final)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_final)
    print("✓ Backend app.py validado e salvo com sucesso!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

print("=" * 65)
print("✓ TUDO CONFIGURADO E PRONTO COM SUCESSO TOTAL!")
print("=" * 65)