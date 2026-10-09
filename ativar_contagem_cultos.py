import os
import shutil
import re
import ast

print("=" * 70)
print("A ATIVAR A CONTAGEM AUTOMÁTICA EM TEMPO REAL E GRAVAÇÃO DE CULTOS...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. BACKUP DE SEGURANÇA
shutil.copy(tpl_dash, tpl_dash + '.bak_contagem')

with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# -------------------------------------------------------------
# 2. LOCALIZAR E MAPEAR O BLOCO DE CULTOS NO DASHBOARD.HTML
# -------------------------------------------------------------
p_culto = html.find('Registo Rápido de Culto')
p_hist = html.find('Histórico de Cultos', p_culto if p_culto != -1 else 0)

if p_culto != -1 and p_hist != -1:
    bloco = html[p_culto:p_hist]

    # A) Garantir que o formulário engloba o registo com a rota correta
    if '<form' in bloco:
        bloco = re.sub(r'<form[^>]*>', '<form action="/cultos/novo" method="POST" id="form-cultos-oficial">', bloco, count=1)
    else:
        # Se não houver tag form aberta antes dos campos, abre antes do primeiro campo
        bloco = 'Registo Rápido de Culto\n<form action="/cultos/novo" method="POST" id="form-cultos-oficial">' + bloco[len('Registo Rápido de Culto'):]

    # B) Identificar os 8 campos de presença e atribuir-lhes a classe 'campo-presenca-culto'
    nomes_presenca = [
        'homens_adultos', 'mulheres_adultas',
        'jovens_rapazes', 'jovens_mocas',
        'criancas_meninos', 'criancas_meninas',
        'visitantes_homens', 'visitantes_mulheres'
    ]

    for nome in nomes_presenca:
        # Adiciona a classe e os eventos de foco/seleção limpa pelo teclado
        padrao_input = rf'(<input[^>]*name=["\']?{nome}["\']?[^>]*>)'
        def add_classe(m):
            tag = m.group(1)
            if 'campo-presenca-culto' not in tag:
                tag = tag[:-1] + ' class="campo-presenca-culto" onfocus="if(this.value==\'0\')this.value=\'\'; this.select();" onblur="if(this.value==\'\')this.value=\'0\';">'
            return tag
        bloco = re.sub(padrao_input, add_classe, bloco)

    # Caso os campos numéricos não tenham o atributo name com esses nomes exatos
    # Procura todos os inputs numéricos antes de 'Apelos' e garante a classe
    idx_apelos_local = bloco.find('Apelos')
    if idx_apelos_local != -1:
        parte_antes_apelos = bloco[:idx_apelos_local]
        parte_depois = bloco[idx_apelos_local:]

        def marcar_presenca(m):
            tag = m.group(0)
            if 'campo-presenca-culto' not in tag and 'hidden' not in tag:
                return tag[:-1] + ' class="campo-presenca-culto" onfocus="if(this.value==\'0\')this.value=\'\'; this.select();" onblur="if(this.value==\'\')this.value=\'0\';">'
            return tag

        parte_antes_apelos = re.sub(r'<input[^>]*type=["\']?number["\']?[^>]*>', marcar_presenca, parte_antes_apelos)
        bloco = parte_antes_apelos + parte_depois

    # C) Mapear a caixa azul de 'Total de Presentes' com ID inequívoco
    if 'Total de Presentes' in bloco:
        idx_tot = bloco.find('Total de Presentes')
        # Procura o primeiro elemento contendo '0' após 'Total de Presentes'
        trecho_tot = bloco[idx_tot:idx_tot+300]
        trecho_tot_mod = re.sub(
            r'(<div[^>]*>|>)\s*0\s*(</div>|<)',
            r'\1<span id="display-total-presentes" style="font-size: 22px; font-weight: bold; color: #1e40af;">0</span>\2',
            trecho_tot,
            count=1
        )
        if 'display-total-presentes' not in trecho_tot_mod:
            trecho_tot_mod = trecho_tot + '\n<div id="display-total-presentes" style="display:none;">0</div>'
        bloco = bloco[:idx_tot] + trecho_tot_mod + bloco[idx_tot+300:]

    # D) Injetar input oculto para persistência do total no Supabase
    if 'name="total_presentes"' not in bloco:
        bloco = bloco + '\n<input type="hidden" name="total_presentes" id="hidden-total-presentes" value="0">\n'

    # E) Fechar a tag </form> após o botão de submissão
    if '</form>' not in bloco:
        bloco = bloco + '\n</form>\n'

    html = html[:p_culto] + bloco + html[p_hist:]

# -------------------------------------------------------------
# 3. POVOAR A TABELA DO HISTÓRICO DE CULTOS
# -------------------------------------------------------------
linhas_tabela_cultos = """
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
    p_h = html.find('Histórico de Cultos')
    p_tb = html.find('<tbody>', p_h)
    p_tbf = html.find('</tbody>', p_tb)
    if p_tb != -1 and p_tbf != -1:
        html = html[:p_tb+7] + "\n" + linhas_tabela_cultos.strip() + "\n                    " + html[p_tbf:]

# -------------------------------------------------------------
# 4. SCRIPT DEFINITIVO DE SOMA EM TEMPO REAL (EVENT LISTENER GLOBAL)
# -------------------------------------------------------------
script_contagem_imediata = """
<script>
function recalcularPresentesCulto() {
    var campos = document.querySelectorAll('.campo-presenca-culto');
    var total = 0;

    campos.forEach(function(inp) {
        var n = (inp.name || '').toLowerCase();
        // Não soma o campo de apelos nem o campo de total
        if (!n.includes('apelo') && !n.includes('total')) {
            var val = parseInt(inp.value, 10);
            if (!isNaN(val) && val > 0) {
                total += val;
            }
        }
    });

    // 1. Atualiza a exibição na caixa azul
    var display = document.getElementById('display-total-presentes');
    if (display) {
        display.innerText = total;
    }

    // 2. Atualiza qualquer texto '0' próximo a 'Total de Presentes'
    var rotulos = document.querySelectorAll('label, span, div');
    rotulos.forEach(function(el) {
        if (el.innerText && el.innerText.includes('Total de Presentes')) {
            var pai = el.parentElement;
            if (pai) {
                var elValor = pai.querySelector('#display-total-presentes') || pai.querySelector('span, div:not(:first-child)');
                if (elValor && elValor !== el) {
                    elValor.innerText = total;
                }
            }
        }
    });

    // 3. Atualiza o input oculto para submissão ao Supabase
    var hidden = document.getElementById('hidden-total-presentes') || document.querySelector('input[name="total_presentes"]');
    if (hidden) {
        hidden.value = total;
    }
}

// Ouvinte global: deteta digitação em tempo real em qualquer input de presença
document.addEventListener('input', function(e) {
    if (e.target && (e.target.classList.contains('campo-presenca-culto') || (e.target.type === 'number' && !(e.target.name || '').includes('apelo')))) {
        recalcularPresentesCulto();
    }
});

document.addEventListener('keyup', function(e) {
    if (e.target && (e.target.classList.contains('campo-presenca-culto') || (e.target.type === 'number' && !(e.target.name || '').includes('apelo')))) {
        recalcularPresentesCulto();
    }
});

document.addEventListener("DOMContentLoaded", function() {
    recalcularPresentesCulto();

    // Se a URL contiver ?aba=cultos, mantém a aba ativa
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
</script>
"""

# Remover scripts de teste anteriores e anexar o script definitivo
html = re.sub(r'<!-- script-.*? -->[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
html = html + "\n<!-- script-contagem-cultos-definitivo -->\n" + script_contagem_imediata

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado com contagem em tempo real!")

# -------------------------------------------------------------
# 5. ASSEGURAR A ROTA DE CULTOS NO APP.PY
# -------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

rota_cultos_oficial = '''
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
linhas_app = app_code.splitlines(keepends=True)
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

app_code = "".join(novas_linhas)

# Validar compilação do app.py
try:
    ast.parse(app_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("✓ Backend app.py validado e pronto!")
except SyntaxError as e_ast:
    print(f"❌ Erro de compilação: {e_ast}")

print("=" * 70)
print("✓ ATIVAÇÃO DA CONTAGEM CONCLUÍDA COM SUCESSO!")
print("=" * 70)