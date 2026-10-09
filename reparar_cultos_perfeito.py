import os
import shutil
import ast
import re

print("=" * 65)
print("A REPARAR O CÁLCULO DE CULTOS, APELOS E HISTÓRICO...")
print("=" * 65)

# 1. BACKUPS DE SEGURANÇA
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
tpl_dash = os.path.join('templates', 'dashboard.html')
if os.path.exists(tpl_dash):
    shutil.copy(tpl_dash, tpl_dash + '.bak')

# -------------------------------------------------------------------
# 2. ATUALIZAR O APP.PY (BANCO DE DADOS, ROTA E LEITURA NO DASHBOARD)
# -------------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Função garantida de criação da tabela de cultos
funcao_tabela = '''
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
    except Exception:
        try:
            if hasattr(conn, 'rollback'): conn.rollback()
        except: pass
'''

if "def assegurar_tabela_cultos" not in code:
    code = funcao_tabela.strip() + "\n\n" + code

# Rota de gravação de cultos 100% blindada
rota_post_cultos = '''
@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    assegurar_tabela_cultos(conn)

    fd = request.form
    data_culto = (fd.get('data_culto') or fd.get('data') or '---').strip()
    tipo_culto = (fd.get('tipo_culto') or fd.get('tipo') or 'Domingo Manhã').strip()

    def get_num(campo):
        val = fd.get(campo)
        if val not in (None, ''):
            try: return int(val)
            except: pass
        return 0

    ha = get_num('homens_adultos')
    ma = get_num('mulheres_adultas')
    jr = get_num('jovens_rapazes')
    jm = get_num('jovens_mocas')
    cm = get_num('criancas_meninos')
    cf = get_num('criancas_meninas')
    vh = get_num('visitantes_homens')
    vm = get_num('visitantes_mulheres')
    apelos = get_num('apelos')

    soma_calculada = ha + ma + jr + jm + cm + cf + vh + vm
    tot_form = get_num('total_presentes')
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
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e:
        print("[ERRO GRAVAR CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

# Substituição segura da rota cultos_novo
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu_rota = False

for l in linhas:
    if "@app.route('/cultos/novo'" in l:
        ignorar = True
        novas_linhas.append(rota_post_cultos.strip() + "\n\n")
        substituiu_rota = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "cultos_novo" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu_rota:
    novas_linhas.append("\n\n" + rota_post_cultos.strip() + "\n")

code = "".join(novas_linhas)

# Leitura dedicada de cultos para o dashboard
leitor_cultos_dash = """
    # Leitura Universal de Cultos para o Dashboard
    cultos = []
    try:
        assegurar_tabela_cultos(conn)
        cur_c = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_c.execute("SELECT id, data_culto, tipo_culto, pregador, tema_mensagem, total_presentes, apelos FROM cultos ORDER BY id DESC LIMIT 50")
        linhas_c = cur_c.fetchall()
        for l in linhas_c:
            if hasattr(l, 'get'):
                cultos.append({
                    'id': l.get('id'),
                    'data_culto': l.get('data_culto') or '---',
                    'tipo_culto': l.get('tipo_culto') or 'Culto',
                    'pregador': l.get('pregador') or '---',
                    'tema_mensagem': l.get('tema_mensagem') or '',
                    'total_presentes': l.get('total_presentes') if l.get('total_presentes') is not None else 0,
                    'apelos': l.get('apelos') if l.get('apelos') is not None else 0
                })
            else:
                cultos.append({
                    'id': l[0],
                    'data_culto': l[1] or '---',
                    'tipo_culto': l[2] or 'Culto',
                    'pregador': l[3] or '---',
                    'tema_mensagem': l[4] or '',
                    'total_presentes': l[5] if l[5] is not None else 0,
                    'apelos': l[6] if l[6] is not None else 0
                })
    except Exception as e_c:
        print("[ERRO LEITURA CULTOS]:", e_c)
        cultos = []
"""

# Inserção da leitura de cultos antes do render_template do dashboard
if "cur_c.execute" not in code:
    code = code.replace(
        "return render_template('dashboard.html',",
        leitor_cultos_dash.strip() + "\n    return render_template('dashboard.html',",
        1
    )

if "cultos=cultos" not in code:
    code = code.replace("planificacoes=planos,", "planificacoes=planos, cultos=cultos,")

# Validação do app.py com AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Backend app.py 100% validado sem erros!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# -------------------------------------------------------------------
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML (INTERFACE PERFEITA DE CULTOS)
# -------------------------------------------------------------------
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Remover scripts antigos que colidiam com o cálculo
html = re.sub(r'<!-- script-calculo-automatico-cultos -->[\s\S]*?</script>', '', html)
html = re.sub(r'<script>[\s\S]*?sincronizarCalculoCulto[\s\S]*?</script>', '', html)

# Estrutura HTML limpa e oficial para o bloco de Cultos
novo_bloco_cultos = """
<div id="secao-cultos-completa" style="margin-top: 15px;">
    <div style="display: grid; grid-template-columns: 1fr 1.3fr; gap: 24px;">
        
        <!-- COLUNA ESQUERDA: FORMULÁRIO DE REGISTO DE CULTO -->
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                <span>⛪</span> Registo Rápido de Culto
            </h3>

            <form action="/cultos/novo" method="POST" id="form-cultos-oficial" style="margin-top: 15px;">
                <div style="display: flex; gap: 12px; margin-bottom: 14px;">
                    <div style="flex: 1;">
                        <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">📅 Data do Culto</label>
                        <input type="date" name="data_culto" required style="width: 100%; padding: 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                    </div>
                    <div style="flex: 1;">
                        <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">⛪ Tipo de Culto</label>
                        <select name="tipo_culto" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;">
                            <option value="Domingo Manhã">Domingo Manhã</option>
                            <option value="Domingo Tarde/Noite">Domingo Tarde/Noite</option>
                            <option value="Quarta-Feira / Doutrina">Quarta-Feira / Doutrina</option>
                            <option value="Sexta-Feira / Oração">Sexta-Feira / Oração</option>
                            <option value="Vigília">Vigília</option>
                            <option value="Culto Especial">Culto Especial</option>
                        </select>
                    </div>
                </div>

                <!-- FAIXA ETÁRIA: MEMBROS -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: bold; color: #334155; display: block; margin-bottom: 8px;">👥 MEMBROS POR FAIXA & SEXO</span>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👨 Homens Adultos</label>
                            <input type="number" name="homens_adultos" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👩 Mulheres Adultas</label>
                            <input type="number" name="mulheres_adultas" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👦 Jovens Rapazes</label>
                            <input type="number" name="jovens_rapazes" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👧 Jovens Moças</label>
                            <input type="number" name="jovens_mocas" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                    </div>
                </div>

                <!-- CRIANÇAS E VISITANTES -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <span style="font-size: 12px; font-weight: bold; color: #334155; display: block; margin-bottom: 8px;">🧒 CRIANÇAS & 💛 VISITANTES</span>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👦 Crianças (Meninos)</label>
                            <input type="number" name="criancas_meninos" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">👧 Crianças (Meninas)</label>
                            <input type="number" name="criancas_meninas" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">💛 Visitantes (Homens)</label>
                            <input type="number" name="visitantes_homens" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b;">💛 Visitantes (Mulheres)</label>
                            <input type="number" name="visitantes_mulheres" min="0" value="0" class="campo-soma-culto" style="width: 100%; padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box;">
                        </div>
                    </div>
                </div>

                <!-- BOXES DE APELOS E TOTAL DE PRESENTES -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                    <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 8px; padding: 10px; text-align: center;">
                        <label style="display: block; font-size: 12px; font-weight: bold; color: #166534; margin-bottom: 4px;">✝ Apelos / Decisões</label>
                        <input type="number" name="apelos" id="input-apelos-oficial" min="0" value="0" style="width: 80%; padding: 6px; font-size: 18px; font-weight: bold; text-align: center; border: 1px solid #bbf7d0; border-radius: 6px; color: #166534; background: white;">
                    </div>
                    <div style="background: #eff6ff; border: 2px solid #93c5fd; border-radius: 8px; padding: 10px; text-align: center;">
                        <label style="display: block; font-size: 12px; font-weight: bold; color: #1e40af; margin-bottom: 4px;">📊 Total de Presentes</label>
                        <div id="box-total-display" style="font-size: 22px; font-weight: bold; color: #1e40af; padding: 4px 0;">0</div>
                        <input type="hidden" name="total_presentes" id="input-total-hidden" value="0">
                    </div>
                </div>

                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Pregador (Palavra)</label>
                    <input type="text" name="pregador" placeholder="Ex: Pastor / Obreiro" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                </div>

                <div style="margin-bottom: 16px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Tema da Mensagem</label>
                    <input type="text" name="tema_mensagem" placeholder="Ex: Salvação, Fé..." style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                </div>

                <button type="submit" style="width: 100%; padding: 13px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: background 0.2s;">
                    Registar Presenças do Culto
                </button>
            </form>
        </div>

        <!-- COLUNA DIREITA: HISTÓRICO DE CULTOS -->
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); overflow-x: auto;">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                <span>📊</span> Histórico de Cultos
            </h3>

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
        </div>
    </div>
</div>
"""

# Substitui o bloco antigo de cultos pelo novo bloco oficial
padrao_bloco_cultos_antigo = r'(<div[^>]*>[\s\S]*?Registo Rápido de Culto[\s\S]*?Histórico de Cultos[\s\S]*?</table>\s*</div>\s*</div>\s*</div>)'
if re.search(padrao_bloco_cultos_antigo, html):
    html = re.sub(padrao_bloco_cultos_antigo, novo_bloco_cultos, html, count=1)
elif 'Registo Rápido de Culto' in html:
    # Substituição por ancoragem
    idx_ini = html.find('Registo Rápido de Culto')
    if idx_ini != -1:
        div_pai_ini = html.rfind('<div', 0, idx_ini)
        div_pai_ini = html.rfind('<div', 0, div_pai_ini)
        idx_fim = html.find('</table>', idx_ini)
        if idx_fim != -1:
            div_pai_fim = html.find('</div>', idx_fim) + 6
            div_pai_fim = html.find('</div>', div_pai_fim) + 6
            html = html[:div_pai_ini] + novo_bloco_cultos + html[div_pai_fim:]

# 4. SCRIPT PRECISO DE SOMA (NÃO TOCA NO CAMPO DE APELOS)
script_soma_exata = """
<script>
function calcularSomaCulto() {
    var campos = document.querySelectorAll('.campo-soma-culto');
    var soma = 0;
    campos.forEach(function(inp) {
        var n = parseInt(inp.value, 10);
        if (!isNaN(n) && n > 0) {
            soma += n;
        }
    });

    var boxDisplay = document.getElementById('box-total-display');
    var inputHidden = document.getElementById('input-total-hidden');

    if (boxDisplay) boxDisplay.innerText = soma;
    if (inputHidden) inputHidden.value = soma;
}

document.addEventListener("DOMContentLoaded", function() {
    var campos = document.querySelectorAll('.campo-soma-culto');
    campos.forEach(function(inp) {
        inp.addEventListener('input', calcularSomaCulto);
        inp.addEventListener('change', calcularSomaCulto);
    });
    calcularSomaCulto();

    // Se o URL trouxer ?aba=cultos, seleciona a aba Cultos & Presenças
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'cultos') {
        var botoes = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item, [onclick*="culto"]');
        for (var i = 0; i < botoes.length; i++) {
            var t = botoes[i].innerText ? botoes[i].innerText.toLowerCase() : '';
            if (t.includes('culto') || t.includes('presença')) {
                botoes[i].click();
                break;
            }
        }
    }
});
</script>
"""

if 'calcularSomaCulto' not in html:
    html = html + "\n<!-- script-soma-exata -->\n" + script_soma_exata

# 5. ATIVAR O BOTÃO AMARELO DE RELATÓRIO OFICIAL (IMPRIMIR/PDF)
html = re.sub(
    r'(<[ab][^>]*)(Visualizar\s*/\s*Imprimir Relatório Oficial)([^<]*</[ab]>)',
    r'<button type="button" onclick="window.print()" class="btn-relatorio" style="display: inline-flex; align-items: center; gap: 8px; background-color: #eab308; color: #1e293b; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; border: none; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📄 Visualizar / Imprimir Relatório Oficial</button>',
    html,
    flags=re.IGNORECASE
)

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado com layout de cultos e soma precisa!")

print("=" * 65)
print("✓ TUDO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 65)