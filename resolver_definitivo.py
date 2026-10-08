import os
import shutil
import ast
import re

print("=" * 65)
print("A REPARAR O SISTEMA PARA A APRESENTAÇÃO DESTA NOITE...")
print("=" * 65)

# 1. BACKUP DE SEGURANÇA DO APP.PY
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
    print("✓ Backup de segurança criado: app.py.bak")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. FUNÇÃO QUE GARANTE A TABELA NO SUPABASE (POSTGRESQL) E SQLITE
funcao_banco = '''
def assegurar_tabela_planificacoes(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        if is_pg:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id SERIAL PRIMARY KEY,
                    departamento TEXT,
                    tipo_evento TEXT,
                    nome_actividade TEXT,
                    data_prevista TEXT,
                    frequencia TEXT,
                    responsavel_directo TEXT,
                    contacto TEXT,
                    status TEXT DEFAULT 'Pendente',
                    igreja_id INTEGER DEFAULT 1
                );
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departamento TEXT,
                    tipo_evento TEXT,
                    nome_actividade TEXT,
                    data_prevista TEXT,
                    frequencia TEXT,
                    responsavel_directo TEXT,
                    contacto TEXT,
                    status TEXT DEFAULT 'Pendente',
                    igreja_id INTEGER DEFAULT 1
                );
            """)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as err:
        try:
            if hasattr(conn, 'rollback'):
                conn.rollback()
        except:
            pass
'''

if "def assegurar_tabela_planificacoes" not in code:
    code = funcao_banco.strip() + "\n\n" + code

# 3. ROTA DA PLANIFICAÇÃO (Suporta gravação com atualização instantânea na tela)
rota_limpa = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import jsonify
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
        igreja_id = session.get('igreja_id', 1)

        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        marcador = "%s" if is_pg else "?"

        sql = f"""INSERT INTO planificacoes 
                  (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status, igreja_id)
                  VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente', {marcador})"""
        
        gravou = False
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto, igreja_id))
            if hasattr(conn, 'commit'):
                conn.commit()
            gravou = True
        except Exception as e:
            print("[ERRO AO GRAVAR PLANO]:", e)
            try:
                if hasattr(conn, 'rollback'):
                    conn.rollback()
            except:
                pass

        # Resposta JSON para atualizar a tabela na hora sem congelar
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                "sucesso": gravou,
                "dados": {
                    "nome_actividade": nome_actividade,
                    "departamento": departamento,
                    "tipo_evento": tipo_evento,
                    "data_prevista": data_prevista,
                    "frequencia": frequencia,
                    "responsavel_directo": responsavel,
                    "contacto": contacto,
                    "status": "Pendente"
                }
            })

        return redirect(request.referrer or '/secretaria/planificacao/nova')

    # Leitura das planificações
    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 50")
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

# Remover todas as versões antigas da rota planificacao_nova
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

# 4. SINCRONIZAR A CONSULTA DO DASHBOARD
code = re.sub(
    r"planos\s*=\s*conn\.execute\([\"']SELECT \* FROM actividades_planeamento.*?\)[\s\S]*?except Exception:\s*planos = \[\]",
    """assegurar_tabela_planificacoes(conn)
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
        planos = []""",
    code
)

if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# 5. VALIDAÇÃO RIGOROSA DA SINTAXE PYTHON COM AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py validado e aprovado pelo compilador Python!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe evitado na linha {e.lineno}: {e}")
    shutil.copy('app.py.bak', 'app.py')
    print("Backup restaurado. O ficheiro app.py está intacto.")
    exit(1)

# 6. SCRIPT JAVASCRIPT EM TEMPO REAL PARA O FORMULÁRIO E TABELA
script_ajax = '''
<script>
(function() {
    var form = document.querySelector('form[action*="/secretaria/planificacao/nova"]');
    if (!form) return;

    var btn = form.querySelector('button[type="submit"]');
    if (btn) {
        btn.removeAttribute('onclick');
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        var submitBtn = form.querySelector('button[type="submit"]');
        var textoAntigo = submitBtn ? submitBtn.innerHTML : 'Gravar Planificação';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '⏳ A gravar na Base de Dados...';
        }

        var formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(res) {
            if (!res.ok) throw new Error('Status: ' + res.status);
            return res.json();
        })
        .then(function(resData) {
            var d = resData.dados || {};

            var tbody = document.querySelector('.coluna-tabela tbody') || document.querySelector('table tbody');
            if (tbody) {
                var linhaVazia = tbody.querySelector('td[colspan]');
                if (linhaVazia) {
                    linhaVazia.closest('tr').remove();
                }

                var tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #eee';
                tr.style.backgroundColor = '#ecfdf5';
                tr.style.transition = 'background-color 2s ease';
                tr.innerHTML = `
                    <td style="padding: 10px;">
                        <strong>${d.nome_actividade || 'Nova Actividade'}</strong><br>
                        <small style="color: gray;">${d.departamento || 'Geral'}</small>
                    </td>
                    <td style="padding: 10px;">${d.data_prevista || '---'}</td>
                    <td style="padding: 10px;">
                        ${d.responsavel_directo || '---'}<br>
                        <small style="color: gray;">${d.contacto || ''}</small>
                    </td>
                    <td style="padding: 10px;">
                        <span style="background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                            Pendente
                        </span>
                    </td>
                    <td style="padding: 10px;">
                        <span style="color: #0d8abc; cursor: pointer; font-size:12px; font-weight:bold;">Ver</span>
                    </td>
                `;
                tbody.insertBefore(tr, tbody.firstChild);

                setTimeout(function() {
                    tr.style.backgroundColor = 'transparent';
                }, 2500);
            }

            if (submitBtn) {
                submitBtn.innerHTML = '✓ Gravado com Sucesso!';
                submitBtn.style.backgroundColor = '#16a34a';
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = textoAntigo;
                    submitBtn.style.backgroundColor = '#3730a3';
                }, 2000);
            }

            var campoNome = form.querySelector('input[name="nome_actividade"]');
            var campoData = form.querySelector('input[name="data_prevista"]');
            var campoResp = form.querySelector('input[name="responsavel_directo"]');
            var campoCont = form.querySelector('input[name="contacto"]');
            if (campoNome) campoNome.value = '';
            if (campoData) campoData.value = '';
            if (campoResp) campoResp.value = '';
            if (campoCont) campoCont.value = '';
        })
        .catch(function(err) {
            console.warn('A usar envio padrão:', err);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = textoAntigo;
            }
            form.submit();
        });
    });
})();
</script>
'''

# 7. APLICAR AS MELHORIAS VISUAIS NOS FICHEIROS HTML
pasta_tpl = 'templates'
if os.path.exists(pasta_tpl):
    for r, _, files in os.walk(pasta_tpl):
        for f_name in files:
            if f_name.endswith('.html'):
                caminho = os.path.join(r, f_name)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html_content = arq.read()

                orig_html = html_content

                html_content = html_content.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html_content = html_content.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')

                # Remove o onclick que causava o bloqueio
                html_content = re.sub(r'onclick="[^"]*this\.form\.submit\(\)[^"]*"', '', html_content)

                if 'action="/secretaria/planificacao/nova"' in html_content:
                    if 'A gravar na Base de Dados' not in html_content:
                        html_content = html_content + "\n" + script_ajax

                if orig_html != html_content:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html_content)
                    print(f"✓ Interface do template atualizada com sucesso: {f_name}")

print("=" * 65)
print("✓ TUDO CONFIGURADO E PRONTO COM SUCESSO ABSOLUTO!")
print("=" * 65)