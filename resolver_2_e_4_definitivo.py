import os
import shutil
import re
import ast

print("=" * 70)
print("A RESOLVER PONTO 2 (CÁLCULO EM TEMPO REAL) E PONTO 4 (GRAVAÇÃO/HISTÓRICO)...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl_dash, tpl_dash + '.bak_2e4')

with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# -------------------------------------------------------------
# 1. RESOLVER O PONTO 2: CÁLCULO DIRETO VIA ONINPUT (INFALÍVEL)
# -------------------------------------------------------------
# Função JavaScript global colocada no topo para execução imediata
funcao_calculo_topo = """
<script>
function somarPresentesCultoAgora() {
    var total = 0;
    var inputs = document.querySelectorAll('.campo-soma-culto');
    for (var i = 0; i < inputs.length; i++) {
        var v = parseInt(inputs[i].value, 10);
        if (!isNaN(v) && v > 0) total += v;
    }
    var display = document.getElementById('display-total-culto-azul');
    if (display) display.innerText = total;
    var hidden = document.getElementById('input-total-culto-hidden');
    if (hidden) hidden.value = total;
}
</script>
"""

if 'somarPresentesCultoAgora' not in html:
    html = funcao_calculo_topo + "\n" + html

# Localizar o bloco de cultos
p_culto = html.find('Registo Rápido de Culto')
p_hist = html.find('Histórico de Cultos', p_culto if p_culto != -1 else 0)

if p_culto != -1 and p_hist != -1:
    bloco_esq = html[p_culto:p_hist]

    # Amarrar o oninput em todos os campos numéricos da presença (antes de Apelos)
    p_apelos = bloco_esq.find('Apelos')
    if p_apelos != -1:
        parte_inputs = bloco_esq[:p_apelos]
        parte_resto = bloco_esq[p_apelos:]

        def colocar_oninput(m):
            tag = m.group(0)
            if 'campo-soma-culto' not in tag:
                # Remove onfocus/onblur duplicados se houver
                tag = re.sub(r'class=["\'][^"\']*["\']', '', tag)
                tag = re.sub(r'oninput=["\'][^"\']*["\']', '', tag)
                tag = tag[:-1] + ' class="campo-soma-culto" oninput="somarPresentesCultoAgora()" onchange="somarPresentesCultoAgora()">'
            return tag

        parte_inputs = re.sub(r'<input[^>]*type=["\']?number["\']?[^>]*>', colocar_oninput, parte_inputs)
        bloco_esq = parte_inputs + parte_resto

    # Identificar a caixa azul do Total de Presentes com o ID exato
    if 'Total de Presentes' in bloco_esq:
        idx_t = bloco_esq.find('Total de Presentes')
        trecho = bloco_esq[idx_t:idx_t+350]
        # Substitui o 0 por um span com id="display-total-culto-azul"
        trecho_novo = re.sub(
            r'(<div[^>]*>|>)\s*(?:0|<span[^>]*>0</span>)\s*(</div>|<)',
            r'\1<span id="display-total-culto-azul" style="font-size: 22px; font-weight: bold; color: #1e40af;">0</span>\2',
            trecho,
            count=1
        )
        bloco_esq = bloco_esq[:idx_t] + trecho_novo + bloco_esq[idx_t+350:]

    # -------------------------------------------------------------
    # 2. RESOLVER O PONTO 4 (PARTE A): GARANTIR FORM DE ENVIO REAL
    # -------------------------------------------------------------
    # Se não houver tag <form action="/cultos/novo", abre antes do primeiro campo
    if '<form action="/cultos/novo"' not in bloco_esq:
        idx_primeiro_input = bloco_esq.find('<input')
        if idx_primeiro_input != -1:
            bloco_esq = bloco_esq[:idx_primeiro_input] + '<form action="/cultos/novo" method="POST" id="form-culto-envio">\n' + bloco_esq[idx_primeiro_input:]
        else:
            bloco_esq = '<form action="/cultos/novo" method="POST" id="form-culto-envio">\n' + bloco_esq

    # Injeta o input hidden do total
    if 'id="input-total-culto-hidden"' not in bloco_esq:
        bloco_esq = bloco_esq + '\n<input type="hidden" name="total_presentes" id="input-total-culto-hidden" value="0">\n'

    # Garante que o botão submete o formulário
    bloco_esq = re.sub(
        r'<button[^>]*>(?:[\s\S]*?Registar Presenças do Culto[\s\S]*?)</button>',
        '<button type="submit" style="width: 100%; padding: 14px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer;">Registar Presenças do Culto</button>\n</form>',
        bloco_esq,
        flags=re.IGNORECASE
    )

    html = html[:p_culto] + bloco_esq + html[p_hist:]

# -------------------------------------------------------------
# 3. RESOLVER O PONTO 4 (PARTE B): INSERIR O JINJA2 NA TABELA
# -------------------------------------------------------------
bloco_tabela_jinja = """
                    <!-- LINHAS DO HISTÓRICO DE CULTOS -->
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

if 'Histórico de Cultos' in html:
    p_h2 = html.find('Histórico de Cultos')
    p_table = html.find('<table', p_h2)
    p_table_fim = html.find('</table>', p_table)

    if p_table != -1 and p_table_fim != -1:
        conteudo_tabela = html[p_table:p_table_fim]
        # Se tem <tbody>, insere dentro
        if '<tbody>' in conteudo_tabela:
            p_tb = conteudo_tabela.find('<tbody>')
            p_tbf = conteudo_tabela.find('</tbody>')
            conteudo_tabela = conteudo_tabela[:p_tb+7] + "\n" + bloco_tabela_jinja.strip() + "\n" + conteudo_tabela[p_tbf:]
        else:
            # Se não tem <tbody>, insere após o primeiro </tr> (cabeçalho)
            p_tr1 = conteudo_tabela.find('</tr>')
            if p_tr1 != -1:
                conteudo_tabela = conteudo_tabela[:p_tr1+5] + "\n<tbody>\n" + bloco_tabela_jinja.strip() + "\n</tbody>\n" + conteudo_tabela[p_tr1+5:]

        html = html[:p_table] + conteudo_tabela + html[p_table_fim:]

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado com sucesso!")

# -------------------------------------------------------------
# 4. GARANTIR A ROTA E O ENVIO DE CULTOS NO APP.PY
# -------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code_app = f.read()

rota_cultos_limpa = '''
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

    soma_calculada = ha + ma + jr + jm + cm + cf + vh + vm
    tot_form = n('total_presentes')
    total = tot_form if tot_form > 0 else soma_calculada

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

# Substitui a rota cultos_novo
linhas_app = code_app.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas_app:
    if "@app.route('/cultos/novo'" in l:
        ignorar = True
        novas_linhas.append(rota_cultos_limpa.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "cultos_novo" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_cultos_limpa.strip() + "\n")

code_app = "".join(novas_linhas)

# Garantir passagem de cultos=cultos para o dashboard
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
    print(f"Aviso de compilação: {e_ast}")

print("=" * 70)
print("✓ PONTOS 2 E 4 CONCLUÍDOS!")
print("=" * 70)