import os
import shutil
import ast
import re

print("=" * 65)
print("A CONFIGURAR O REGISTO DE CULTOS E O BOTÃO DE RELATÓRIO...")
print("=" * 65)

# 1. BACKUPS DE SEGURANÇA
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
tpl_dash = os.path.join('templates', 'dashboard.html')
if os.path.exists(tpl_dash):
    shutil.copy(tpl_dash, tpl_dash + '.bak')

# -------------------------------------------------------------------
# 2. ATUALIZAR O APP.PY (CRIAR TABELA CULTOS, ROTA POST E LEITURA)
# -------------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Função que garante a tabela 'cultos' no Supabase / PostgreSQL / SQLite
funcao_tabela_cultos = '''
def assegurar_tabela_cultos(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
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
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e_c:
        try:
            if hasattr(conn, 'rollback'): conn.rollback()
        except: pass
'''

if "def assegurar_tabela_cultos" not in code:
    code = funcao_tabela_cultos.strip() + "\n\n" + code

# Rota para receber a submissão do formulário de cultos
rota_cultos_post = '''
@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    assegurar_tabela_cultos(conn)

    fd = request.form
    data_culto = (fd.get('data_culto') or fd.get('data') or '---').strip()
    tipo_culto = (fd.get('tipo_culto') or fd.get('tipo') or 'Domingo Manhã').strip()

    def to_int(v):
        try: return int(v)
        except: return 0

    ha = to_int(fd.get('homens_adultos'))
    ma = to_int(fd.get('mulheres_adultas'))
    jr = to_int(fd.get('jovens_rapazes'))
    jm = to_int(fd.get('jovens_mocas'))
    c_meninos = to_int(fd.get('criancas_meninos'))
    c_meninas = to_int(fd.get('criancas_meninas'))
    v_homens = to_int(fd.get('visitantes_homens'))
    v_mulheres = to_int(fd.get('visitantes_mulheres'))
    apelos = to_int(fd.get('apelos'))

    # Cálculo seguro do total
    calc_total = ha + ma + jr + jm + c_meninos + c_meninas + v_homens + v_mulheres
    total = to_int(fd.get('total_presentes'))
    if total == 0 and calc_total > 0:
        total = calc_total

    pregador = (fd.get('pregador') or '---').strip()
    tema_mensagem = (fd.get('tema_mensagem') or '').strip()

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
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, c_meninos, c_meninas, v_homens, v_mulheres, apelos, total, pregador, tema_mensagem))
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as err:
        print("[ERRO GRAVACAO CULTO]:", err)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

if "@app.route('/cultos/novo'" not in code:
    code = code + "\n\n" + rota_cultos_post.strip() + "\n"

# Injetar leitura de 'cultos' dentro da função dashboard()
leitura_cultos_sql = """
    # Leitura Universal de Cultos para o Dashboard
    cultos = []
    try:
        assegurar_tabela_cultos(conn)
        cur_clt = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_clt.execute("SELECT id, data_culto, tipo_culto, pregador, tema_mensagem, total_presentes, apelos FROM cultos ORDER BY id DESC LIMIT 50")
        linhas_clt = cur_clt.fetchall()
        for l in linhas_clt:
            if hasattr(l, 'get'):
                cultos.append({
                    'id': l.get('id'),
                    'data_culto': l.get('data_culto') or '---',
                    'tipo_culto': l.get('tipo_culto') or 'Culto',
                    'pregador': l.get('pregador') or '---',
                    'tema_mensagem': l.get('tema_mensagem') or '',
                    'total_presentes': l.get('total_presentes') or 0,
                    'apelos': l.get('apelos') or 0
                })
            else:
                cultos.append({
                    'id': l[0],
                    'data_culto': l[1] or '---',
                    'tipo_culto': l[2] or 'Culto',
                    'pregador': l[3] or '---',
                    'tema_mensagem': l[4] or '',
                    'total_presentes': l[5] or 0,
                    'apelos': l[6] or 0
                })
    except Exception as e_clt:
        print("[AVISO LEITURA CULTOS]:", e_clt)
        cultos = []
"""

if "cultos = []" not in code or "cur_clt.execute" not in code:
    code = code.replace(
        "return render_template('dashboard.html',",
        leitura_cultos_sql.strip() + "\n    return render_template('dashboard.html',",
        1
    )

if "cultos=cultos" not in code:
    code = code.replace("planificacoes=planos,", "planificacoes=planos, cultos=cultos,")

# Validação com compilador Python (AST)
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py atualizado e validado sem erros!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# -------------------------------------------------------------------
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML
# -------------------------------------------------------------------
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# A) Ativar o botão amarelo "Visualizar / Imprimir Relatório Oficial"
html = re.sub(
    r'(<[ab][^>]*)(Visualizar\s*/\s*Imprimir Relatório Oficial)([^<]*</[ab]>)',
    r'<button type="button" onclick="imprimirRelatorioOficial()" class="btn-relatorio" style="display: inline-flex; align-items: center; gap: 8px; background-color: #eab308; color: #1e293b; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; border: none; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📄 Visualizar / Imprimir Relatório Oficial</button>',
    html,
    flags=re.IGNORECASE
)

# B) Corrigir o formulário de Cultos
# Garantir action="/cultos/novo" e method="POST"
if 'Registo Rápido de Culto' in html:
    # Ajusta o form que engloba o bloco de culto
    padrao_form_culto = r'(<div[^>]*>[\s\S]*?Registo Rápido de Culto[\s\S]*?<form)([^>]*>)'
    
    def repl_form_culto(m):
        tag_abertura = m.group(1)
        resto = m.group(2)
        if 'action=' in resto:
            resto = re.sub(r'action=["\'][^"\']*["\']', 'action="/cultos/novo"', resto)
        else:
            resto = ' action="/cultos/novo"' + resto
        if 'method=' in resto:
            resto = re.sub(r'method=["\'][^"\']*["\']', 'method="POST"', resto)
        else:
            resto = ' method="POST"' + resto
        return tag_abertura + resto

    html = re.sub(padrao_form_culto, repl_form_culto, html, count=1)

    # Corrigir o botão dentro do bloco de culto: de "Gravar Planificação" para "Registar Culto"
    bloco_culto_match = re.search(r'Registo Rápido de Culto[\s\S]*?Histórico de Cultos', html)
    if bloco_culto_match:
        bloco_antigo = bloco_culto_match.group(0)
        bloco_novo = bloco_antigo.replace('Gravar Planificação', 'Registar Presenças do Culto')
        html = html.replace(bloco_antigo, bloco_novo)

# C) Garantir a exibição da tabela Histórico de Cultos
tabela_cultos_html = """
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 2px solid #e2e8f0; text-align: left; color: #475569;">
                        <th style="padding: 10px 8px;">Data/Culto</th>
                        <th style="padding: 10px 8px;">Pregador</th>
                        <th style="padding: 10px 8px;">Total</th>
                        <th style="padding: 10px 8px;">Apelos</th>
                    </tr>
                </thead>
                <tbody>
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
                </tbody>
            </table>
"""

# Substitui o miolo da tabela de Histórico de Cultos caso esteja vazia
if 'Histórico de Cultos' in html:
    padrao_tabela_vazia = r'(<h[234][^>]*>\s*(?:📊\s*)?Histórico de Cultos\s*</h[234]>[\s\S]*?)(<table[\s\S]*?</table>)'
    if re.search(padrao_tabela_vazia, html):
        html = re.sub(padrao_tabela_vazia, r'\1' + tabela_cultos_html.strip(), html, count=1)

# D) Script de impressão oficial e suporte à aba 'cultos'
script_cultos_e_print = """
<script>
function imprimirRelatorioOficial() {
    window.print();
}

document.addEventListener("DOMContentLoaded", function() {
    // Abertura automática da aba se a URL trouxer ?aba=cultos
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'cultos') {
        var links = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item, [onclick*="culto"]');
        for (var i = 0; i < links.length; i++) {
            var txt = links[i].innerText ? links[i].innerText.toLowerCase() : '';
            if (txt.includes('culto') || txt.includes('presença')) {
                links[i].click();
                break;
            }
        }
    }
});
</script>

<style>
@media print {
    .sidebar, .sidebar-item, nav, aside, .btn-relatorio, button, form {
        display: none !important;
    }
    main, .container, body {
        margin: 0 !important;
        padding: 15px !important;
        background: white !important;
        color: black !important;
        width: 100% !important;
    }
    table {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    th, td {
        border: 1px solid #ddd !important;
        padding: 8px !important;
    }
}
</style>
"""

if 'imprimirRelatorioOficial' not in html:
    html = html + "\n<!-- script-cultos-e-relatorio -->\n" + script_cultos_e_print

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado com sucesso!")

print("=" * 65)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 65)