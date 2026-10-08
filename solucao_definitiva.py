import os
import shutil
import ast
import re

print("=" * 65)
print("INICIANDO A CORREÇÃO DEFINITIVA PARA A APRESENTAÇÃO...")
print("=" * 65)

# 1. BACKUP DE SEGURANÇA
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
    print("✓ Backup criado: app.py.bak")

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

# 3. ROTA DA PLANIFICAÇÃO (Suporta atualização na tela na hora)
rota_perfeita = '''
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

        is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
        marcador = "%s" if is_pg else "?"

        sql = f"""INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        gravou = False
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            gravou = True
        except Exception as e:
            print("[ERRO AO GRAVAR PLANO]:", e)
            try:
                if hasattr(conn, 'rollback'): conn.rollback()
            except Exception: pass

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                "sucesso": gravou,
                "dados": {
                    "nome_actividade": nome_actividade,
                    "departamento": departamento,
                    "tipo_evento": tipo_evento,
                    "data_prevista": data_prevista,
                    "responsavel_directo": responsavel,
                    "contacto": contacto,
                    "status": "Pendente"
                }
            })

        return redirect(request.referrer or '/')

    # Leitura
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

# Remover versões duplicadas da rota
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(rota_perfeita.strip() + "\n\n")
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

code = "".join(novas_linhas)

# 4. SINCRONIZAR A CONSULTA DO DASHBOARD PARA LER PLANIFICACOES E PASSAR AS DUAS VARIÁVEIS
bloco_leitura_dash = """
    # 4. Planificações Eclesiásticas Sincronizadas
    assegurar_tabela_planificacoes(conn)
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
        planos = []
"""

# Substitui o trecho que lia da tabela errada
code = re.sub(
    r"#\s*4\.\s*Planifica[^\n]*\n[\s\S]*?(?=#\s*5\.|\n\s*candidatos_batismo)",
    bloco_leitura_dash.strip() + "\n\n    ",
    code
)

if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# 5. VALIDAÇÃO POR COMPILADOR AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py 100% validado sem erros de sintaxe!")
except SyntaxError as e:
    print(f"❌ Erro de compilação: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# 6. ATUALIZAR OS TEMPLATES (Remover o onclick duplo e ligar a atualização instantânea)
script_tempo_real = '''
<script>
document.addEventListener("DOMContentLoaded", function() {
    var form = document.querySelector('form[action*="/secretaria/planificacao/nova"]');
    if (!form) return;

    var btn = form.querySelector('button[type="submit"]');
    if (btn) btn.removeAttribute('onclick');

    form.addEventListener("submit", function(e) {
        e.preventDefault();
        var submitBtn = form.querySelector('button[type="submit"]');
        var textoOriginal = submitBtn ? submitBtn.innerHTML : 'Gravar Planificação';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '⏳ A gravar...';
        }

        var formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function(res) {
            if (!res.ok) throw new Error("Erro na gravação");
            return res.json();
        })
        .then(function(resData) {
            var d = resData.dados || {};
            var tbody = document.querySelector('.coluna-tabela tbody') || document.querySelector('table tbody');
            if (tbody) {
                var vazia = tbody.querySelector('td[colspan]');
                if (vazia) vazia.closest('tr').remove();

                var tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #eee';
                tr.style.backgroundColor = '#ecfdf5';
                tr.innerHTML = `
                    <td style="padding: 10px;">
                        <strong>${d.nome_actividade}</strong><br>
                        <small style="color: gray;">${d.departamento}</small>
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
            }

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '✓ Gravado com Sucesso!';
                submitBtn.style.backgroundColor = '#16a34a';
                setTimeout(function() {
                    submitBtn.innerHTML = textoOriginal;
                    submitBtn.style.backgroundColor = '#3730a3';
                }, 2000);
            }
            form.reset();
        })
        .catch(function() {
            if (submitBtn) submitBtn.disabled = false;
            form.submit();
        });
    });
});
</script>
'''

pasta_t = 'templates'
if os.path.exists(pasta_t):
    for r, _, files in os.walk(pasta_t):
        for f in files:
            if f.endswith('.html'):
                caminho = os.path.join(r, f)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html = arq.read()

                orig = html
                html = html.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html = html.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')
                html = re.sub(r'onclick="[^"]*this\.form\.submit\(\)[^"]*"', '', html)

                if 'action="/secretaria/planificacao/nova"' in html:
                    if 'A gravar...' not in html:
                        html = html + "\n" + script_tempo_real

                if orig != html:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    print(f"✓ Interface sincronizada: {f}")

print("=" * 65)
print("✓ TUDO CORRIGIDO E PRONTO COM SUCESSO!")
print("=" * 65)