import os
import subprocess
import re
import ast

print("=" * 65)
print("A RESTAURAR O DESIGN ORIGINAL E A RESOLVER OS CULTOS...")
print("=" * 65)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. LOCALIZAR NO GIT O COMMIT COM O LAYOUT ELEGANTE E INTACTO
res_log = subprocess.run(['git', 'log', '--format=%H %s', '-40'], capture_output=True, text=True)
commits = [c.strip() for c in res_log.stdout.strip().split('\n') if c.strip()]

commit_escolhido = None
for c in commits:
    partes = c.split(maxsplit=1)
    h = partes[0]
    msg = partes[1] if len(partes) > 1 else ''
    if "Liberar navegacao" in msg:
        commit_escolhido = h
        print(f"✓ Encontrado commit do layout íntegro: {h[:7]} ('{msg}')")
        break

if not commit_escolhido:
    for c in commits:
        partes = c.split(maxsplit=1)
        h = partes[0]
        msg = partes[1] if len(partes) > 1 else ''
        if any(t in msg for t in ["Unificar modulo", "Adicionar navegacao"]):
            commit_escolhido = h
            print(f"✓ Commit base alternativo identificado: {h[:7]} ('{msg}')")
            break

if not commit_escolhido:
    print("❌ Não foi possível identificar o commit automaticamente.")
    exit(1)

# Extrai o dashboard.html original do commit intacto
html_original = subprocess.check_output(['git', 'show', f'{commit_escolhido}:templates/dashboard.html'], text=True, encoding='utf-8')
print(f"✓ Ficheiro dashboard.html restaurado na íntegra ({len(html_original.splitlines())} linhas)!")

# -------------------------------------------------------------
# 2. AJUSTES CIRÚRGICOS (SEM ALTERAR QUALQUER DIV OU CSS DE LAYOUT)
# -------------------------------------------------------------

# A) Ativar o botão amarelo de relatório na Secretaria
html_original = re.sub(
    r'(<[ab][^>]*)(Visualizar\s*/\s*Imprimir Relatório Oficial)([^<]*</[ab]>)',
    r'<button type="button" onclick="window.print()" class="btn-relatorio" style="display: inline-flex; align-items: center; gap: 8px; background-color: #eab308; color: #1e293b; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; border: none; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📄 Visualizar / Imprimir Relatório Oficial</button>',
    html_original,
    flags=re.IGNORECASE
)

# B) Corrigir o formulário de culto: rota e botão
# Garante que o form de cultos aponta para /cultos/novo
if 'Registo Rápido de Culto' in html_original:
    # Ajusta a tag <form> que envolve o registo de culto
    p_culto = html_original.find('Registo Rápido de Culto')
    p_form = html_original.find('<form', p_culto)
    if p_form != -1 and p_form - p_culto < 300:
        p_form_fim = html_original.find('>', p_form)
        tag_form_antiga = html_original[p_form:p_form_fim+1]
        tag_form_nova = '<form action="/cultos/novo" method="POST" id="form-culto-real">'
        html_original = html_original[:p_form] + tag_form_nova + html_original[p_form_fim+1:]

    # Ajusta o botão de submit do culto (de "Gravar Planificação" para "Registar Presenças do Culto")
    bloco_c = html_original[p_culto:p_culto+4500]
    if 'Gravar Planificação' in bloco_c:
        bloco_c_ajustado = bloco_c.replace('Gravar Planificação', 'Registar Presenças do Culto', 1)
        html_original = html_original[:p_culto] + bloco_c_ajustado + html_original[p_culto+4500:]

# C) Garantir a exibição dos cultos na tabela do histórico
tabela_linhas_cultos = """
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

if 'Histórico de Cultos' in html_original:
    p_hist = html_original.find('Histórico de Cultos')
    p_tbody = html_original.find('<tbody>', p_hist)
    p_tbody_fim = html_original.find('</tbody>', p_tbody)
    if p_tbody != -1 and p_tbody_fim != -1:
        html_original = html_original[:p_tbody+7] + "\n" + tabela_linhas_cultos.strip() + "\n" + html_original[p_tbody_fim:]

# D) Script leve para soma do total e navegação (sem bloquear digitação)
script_limpo = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var formCulto = document.getElementById('form-culto-real') || document.querySelector('form[action*="cultos"]');
    if (formCulto) {
        var camposPresenca = [
            'homens_adultos', 'mulheres_adultas', 
            'jovens_rapazes', 'jovens_mocas', 
            'criancas_meninos', 'criancas_meninas', 
            'visitantes_homens', 'visitantes_mulheres'
        ];

        function recalcularTotal() {
            var soma = 0;
            camposPresenca.forEach(function(nome) {
                var inp = formCulto.querySelector('input[name*="' + nome + '"]');
                if (inp) {
                    var v = parseInt(inp.value, 10);
                    if (!isNaN(v) && v > 0) soma += v;
                }
            });

            // Atualiza apenas o Total de Presentes
            var hiddenTot = formCulto.querySelector('input[name="total_presentes"]');
            if (hiddenTot) hiddenTot.value = soma;

            var displays = formCulto.querySelectorAll('div, span, strong, input');
            displays.forEach(function(el) {
                if (el.id === 'box-total-display' || el.id === 'display-total') {
                    el.innerText = soma;
                }
            });

            // Caso a caixa azul seja um elemento de texto próximo de 'Total de Presentes'
            var labels = formCulto.querySelectorAll('label, span, div');
            labels.forEach(function(lb) {
                if (lb.innerText && lb.innerText.includes('Total de Presentes')) {
                    var container = lb.parentElement;
                    if (container) {
                        var valBox = container.querySelector('div:not(:first-child), strong');
                        if (valBox) valBox.innerText = soma;
                    }
                }
            });
        }

        // Apenas ouve o evento input sem interferir no teclado ou no campo de apelos
        camposPresenca.forEach(function(nome) {
            var inp = formCulto.querySelector('input[name*="' + nome + '"]');
            if (inp) {
                inp.addEventListener('input', recalcularTotal);
            }
        });
    }

    // Abertura automática da aba se a URL contiver ?aba=
    var params = new URLSearchParams(window.location.search);
    var aba = params.get('aba');
    if (aba) {
        var links = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item');
        for (var i = 0; i < links.length; i++) {
            var txt = links[i].innerText ? links[i].innerText.toLowerCase() : '';
            if (txt.includes(aba)) {
                links[i].click();
                break;
            }
        }
    }
});
</script>
"""

# Remove scripts de teste anteriores e anexa o script limpo
html_original = re.sub(r'<!-- script-.*?cultos -->[\s\S]*?</script>', '', html_original)
html_original = html_original + "\n" + script_limpo

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html_original)
print("✓ templates/dashboard.html atualizado e salvo com layout perfeito!")

# -------------------------------------------------------------
# 3. ATUALIZAR O APP.PY (ROTA SEGURA E LEITURA DE CULTOS)
# -------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code_app = f.read()

rota_cultos_segura = '''
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

# Substitui a rota no app.py
linhas_app = code_app.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas_app:
    if "@app.route('/cultos/novo'" in l:
        ignorar = True
        novas_linhas.append(rota_cultos_segura.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "cultos_novo" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + rota_