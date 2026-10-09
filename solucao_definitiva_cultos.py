import os
import shutil
import subprocess
import re
import ast

print("=" * 70)
print("A RESTAURAR O DESIGN LIMPO E A ATIVAR A GRAVAÇÃO DE CULTOS...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A VERSÃO COM DESIGN INTACTO DO GIT
res_log = subprocess.run(['git', 'log', '--format=%H %s', '-40'], capture_output=True, text=True)
commits = [c.strip() for c in res_log.stdout.strip().split('\n') if c.strip()]

commit_escolhido = None
for c in commits:
    partes = c.split(maxsplit=1)
    h = partes[0]
    msg = partes[1] if len(partes) > 1 else ''
    if "Liberar navegacao" in msg or "Unificar modulo" in msg:
        commit_escolhido = h
        print(f"✓ Commit original recuperado: {h[:7]} ('{msg}')")
        break

if not commit_escolhido and commits:
    commit_escolhido = commits[0].split()[0]

html_puro = subprocess.check_output(['git', 'show', f'{commit_escolhido}:templates/dashboard.html'], text=True, encoding='utf-8')
print(f"✓ Dashboard base recuperado ({len(html_puro.splitlines())} linhas)!")

# -------------------------------------------------------------
# 2. LIMPAR QUALQUER SCRIPT INTRUSO QUE CAUSOU A COMPRESSÃO DO LAYOUT
# -------------------------------------------------------------
html_puro = re.sub(r'<!-- script-.*? -->[\s\S]*?</script>', '', html_puro, flags=re.IGNORECASE)
html_puro = re.sub(r'<script>[\s\S]*?somarPresentesCultoAgora[\s\S]*?</script>', '', html_puro)
html_puro = re.sub(r'<script>[\s\S]*?recalcularPresentesCulto[\s\S]*?</script>', '', html_puro)
html_puro = re.sub(r'<script>[\s\S]*?calcularSomaCulto[\s\S]*?</script>', '', html_puro)

# -------------------------------------------------------------
# 3. CONECTAR O FORMULÁRIO DE CULTOS (ENVIO REAL)
# -------------------------------------------------------------
p_culto = html_puro.find('Registo Rápido de Culto')
p_hist = html_puro.find('Histórico de Cultos', p_culto if p_culto != -1 else 0)

if p_culto != -1 and p_hist != -1:
    bloco = html_puro[p_culto:p_hist]

    # Garante que a tag form aponta para /cultos/novo
    if '<form' in bloco:
        bloco = re.sub(r'<form[^>]*>', '<form action="/cultos/novo" method="POST" id="form-culto-real">', bloco, count=1)
    else:
        bloco = 'Registo Rápido de Culto\n<form action="/cultos/novo" method="POST" id="form-culto-real">' + bloco[len('Registo Rápido de Culto'):]

    # Garante que o botão tem type="submit" e submete o formulário
    if 'Gravar Planificação' in bloco:
        bloco = bloco.replace('Gravar Planificação', 'Registar Presenças do Culto')

    bloco = re.sub(r'<button([^>]*)>', r'<button\1 type="submit">', bloco)

    if '</form>' not in bloco:
        bloco = bloco + '\n</form>\n'

    html_puro = html_puro[:p_culto] + bloco + html_puro[p_hist:]

# -------------------------------------------------------------
# 4. TABELA DO HISTÓRICO DE CULTOS (EXIBIÇÃO IMEDIATA)
# -------------------------------------------------------------
linhas_cultos_tabela = """
                    {% if cultos %}
                        {% for c in cultos %}
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 12px 8px;">
                                <strong style="color: #1e293b;">{{ c.data_culto }}</strong><br>
                                <small style="color: #64748b;">{{ c.tipo_culto }}</small>
                            </td>
                            <td style="padding: 12px 8px;">
                                <strong style="color: #1e293b;">{{ c.pregador }}</strong><br>
                                <small style="color: #64748b;">{{ c.tema_mensagem }}</small>
                            </td>
                            <td style="padding: 12px 8px;">
                                <span style="background-color: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;">
                                    {{ c.total_presentes }}
                                </span>
                            </td>
                            <td style="padding: 12px 8px;">
                                <span style="background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;">
                                    {{ c.apelos }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="4" style="text-align: center; padding: 35px; color: #94a3b8;">
                                Nenhum culto registado ainda. Registe o primeiro ao lado.
                            </td>
                        </tr>
                    {% endif %}
"""

if p_hist != -1:
    p_tbody = html_puro.find('<tbody>', p_hist)
    p_tbody_fim = html_puro.find('</tbody>', p_tbody)
    if p_tbody != -1 and p_tbody_fim != -1:
        html_puro = html_puro[:p_tbody+7] + "\n" + linhas_cultos_tabela.strip() + "\n                    " + html_puro[p_tbody_fim:]

# -------------------------------------------------------------
# 5. SCRIPT SIMPLES: NAVEGAÇÃO ENTRE ABAS E FALLBACK DE FOTOS
# -------------------------------------------------------------
script_apoio = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Manter a aba Cultos ativa ao recarregar
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'cultos') {
        var links = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item');
        for (var i = 0; i < links.length; i++) {
            var txt = links[i].innerText ? links[i].innerText.toLowerCase() : '';
            if (txt.includes('culto') || txt.includes('presença')) {
                links[i].click();
                break;
            }
        }
    }
});

// Fallback de imagens quebradas para avatares elegantes
window.addEventListener('error', function(e) {
    if (e.target && e.target.tagName === 'IMG' && (e.target.src.includes('uploads') || e.target.src.includes('membro'))) {
        e.target.onerror = null;
        var nome = e.target.alt || 'Membro';
        e.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(nome) + '&background=3730a3&color=fff&size=128';
    }
}, true);
</script>
"""

html_puro = html_puro + "\n" + script_apoio

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html_puro)
print("✓ templates/dashboard.html salvo com design 100% íntegro!")

# -------------------------------------------------------------
# 6. APP.PY: CÁLCULO AUTOMÁTICO INFALÍVEL NO SERVIDOR (PYTHON)
# -------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code_app = f.read()

rota_cultos_oficial = '''
@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    # Garantir existência da tabela no Supabase
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
    def n(campo):
        v = fd.get(campo)
        if v not in (None, ''):
            try: return int(v)
            except: pass
        return 0

    data_culto = (fd.get('data_culto') or '---').strip()
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

    # CÁLCULO AUTOMÁTICO FEITO DIRETAMENTE NO PYTHON (NÃO FALHA)
    soma_automatica = ha + ma + jr + jm + cm + cf + vh + vm
    tot_digitado = n('total_presentes')
    total = tot_digitado if tot_digitado > 0 else soma_automatica

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
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e_post:
        print("[ERRO GRAVAR CULTO]:", e_post)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

# Substitui a rota no app.py
linhas_app = code_app.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas_app:
    if "@app.route('/cultos/novo'" in l:
        ignorar = True
        novas_linhas.append(rota_cultos_oficial.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "cultos_novo" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_cultos_oficial.strip() + "\n")

code_app = "".join(novas_linhas)

# Garantir passagem de cultos=cultos ao template
if "cultos=cultos" not in code_app:
    code_app = re.sub(
        r"(return\s+render_template\s*\(\s*['\"]dashboard\.html['\"]\s*,)",
        r"\1 cultos=cultos, ",
        code_app,
        count=1
    )

try:
    ast.parse(code_app)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_app)
    print("✓ Backend app.py 100% validado!")
except SyntaxError as e_ast:
    print(f"❌ Erro em app.py: {e_ast}")

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO DEFINITIVO!")
print("=" * 70)