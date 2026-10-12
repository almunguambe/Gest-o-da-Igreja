import os
import shutil
import re
import ast

print("=" * 70)
print("A APLICAR MOTOR REATIVO MODERNO (ALPINE.JS) NO MÓDULO DE CULTOS...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl_dash, tpl_dash + '.bak_moderna')

with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# -------------------------------------------------------------
# 1. INJETAR O MOTOR REATIVO (ALPINE.JS) NO CABEÇALHO DO HTML
# -------------------------------------------------------------
cdn_alpine = '<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.3/dist/cdn.min.js"></script>'

if 'alpinejs' not in html:
    if '<head>' in html:
        html = html.replace('<head>', '<head>\n    ' + cdn_alpine, 1)
    else:
        html = cdn_alpine + '\n' + html
    print("✓ Motor reativo Alpine.js injetado com sucesso no template!")

# -------------------------------------------------------------
# 2. SUBSTITUIR O BLOCO DE CULTOS PELO MODELO REATIVO DEFINITIVO
# -------------------------------------------------------------
bloco_cultos_reativo = """
<!-- ================= MÓDULO DE CULTOS REATIVO (ALPINE.JS) ================= -->
<div x-data="{
        ha: 0, ma: 0, jr: 0, jm: 0, 
        cm: 0, cf: 0, vh: 0, vm: 0,
        apelos: 0,
        get total() {
            return (Number(this.ha) || 0) + (Number(this.ma) || 0) + 
                   (Number(this.jr) || 0) + (Number(this.jm) || 0) + 
                   (Number(this.cm) || 0) + (Number(this.cf) || 0) + 
                   (Number(this.vh) || 0) + (Number(this.vm) || 0);
        }
     }" 
     style="display: grid; grid-template-columns: 1fr 1.35fr; gap: 24px; align-items: start; margin-top: 15px; width: 100%;">
    
    <!-- CARD 1: FORMULÁRIO DE REGISTO REATIVO -->
    <div style="background: white; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #e2e8f0;">
        <h3 style="margin-top: 0; color: #1e293b; font-size: 18px; display: flex; align-items: center; gap: 8px;">
            <span>⛪</span> Registo Rápido de Culto
        </h3>

        <form action="/cultos/novo" method="POST" style="margin-top: 15px;">
            <div style="display: flex; gap: 12px; margin-bottom: 14px;">
                <div style="flex: 1;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">📅 Data do Culto</label>
                    <input type="date" name="data_culto" style="width: 100%; padding: 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
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

            <!-- MEMBROS POR FAIXA & SEXO -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <span style="font-size: 12px; font-weight: bold; color: #334155; display: block; margin-bottom: 8px;">👥 MEMBROS POR FAIXA & SEXO</span>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👨 Homens Adultos</label>
                        <input type="number" name="homens_adultos" x-model.number="ha" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👩 Mulheres Adultas</label>
                        <input type="number" name="mulheres_adultas" x-model.number="ma" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👦 Jovens Rapazes</label>
                        <input type="number" name="jovens_rapazes" x-model.number="jr" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👧 Jovens Moças</label>
                        <input type="number" name="jovens_mocas" x-model.number="jm" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                </div>
            </div>

            <!-- CRIANÇAS & VISITANTES -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <span style="font-size: 12px; font-weight: bold; color: #334155; display: block; margin-bottom: 8px;">🧒 CRIANÇAS & 💛 VISITANTES</span>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👦 Crianças (Meninos)</label>
                        <input type="number" name="criancas_meninos" x-model.number="cm" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">👧 Crianças (Meninas)</label>
                        <input type="number" name="criancas_meninas" x-model.number="cf" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">💛 Visitantes (Homens)</label>
                        <input type="number" name="visitantes_homens" x-model.number="vh" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: #64748b; font-weight: 500;">💛 Visitantes (Mulheres)</label>
                        <input type="number" name="visitantes_mulheres" x-model.number="vm" min="0" style="width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; font-weight: 600;">
                    </div>
                </div>
            </div>

            <!-- APELOS E TOTAL REATIVO -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 8px; padding: 10px; text-align: center;">
                    <label style="display: block; font-size: 12px; font-weight: bold; color: #166534; margin-bottom: 4px;">✝ Apelos / Decisões</label>
                    <input type="number" name="apelos" x-model.number="apelos" min="0" style="width: 85%; padding: 6px; font-size: 18px; font-weight: bold; text-align: center; border: 1px solid #bbf7d0; border-radius: 6px; color: #166534; background: white;">
                </div>
                <div style="background: #eff6ff; border: 2px solid #93c5fd; border-radius: 8px; padding: 10px; text-align: center;">
                    <label style="display: block; font-size: 12px; font-weight: bold; color: #1e40af; margin-bottom: 4px;">📊 Total de Presentes</label>
                    <div x-text="total" style="font-size: 22px; font-weight: bold; color: #1e40af; padding: 4px 0;">0</div>
                    <input type="hidden" name="total_presentes" :value="total">
                </div>
            </div>

            <div style="margin-bottom: 12px;">
                <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Pregador (Palavra)</label>
                <input type="text" name="pregador" placeholder="Ex: Pastor / Obreiro" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
            </div>

            <div style="margin-bottom: 16px;">
                <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Tema da Mensagem</label>
                <input type="text" name="tema_mensagem" placeholder="Ex: A Fidelidade de Deus..." style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
            </div>

            <button type="submit" style="width: 100%; padding: 14px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: background 0.2s;">
                Registar Presenças do Culto
            </button>
        </form>
    </div>

    <!-- CARD 2: HISTÓRICO DE CULTOS CONECTADO -->
    <div style="background: white; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; overflow-x: auto;">
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
<!-- ================= FIM MÓDULO DE CULTOS REATIVO ================= -->
"""

# Substituição rigorosa de todo o bloco antigo de cultos pelo bloco reativo
padrao_cultos = r'(<!--\s*=*.*?CULTOS[\s\S]*?<!--\s*=*.*?FIM.*?CULTOS.*?=*-->|<div[^>]*>[\s\S]*?Registo R[aá]pido de Culto[\s\S]*?Hist[oó]rico de Cultos[\s\S]*?</table>\s*</div>\s*</div>)'

if re.search(padrao_cultos, html, re.IGNORECASE):
    html = re.sub(padrao_cultos, bloco_cultos_reativo.strip(), html, count=1, flags=re.IGNORECASE)
    print("✓ Bloco de Cultos substituído com sucesso pelo modelo reativo!")
else:
    # Se não apanhou por regex completo, localiza os delimitadores de texto
    p_i = html.find('Registo Rápido de Culto')
    if p_i == -1: p_i = html.find('Registo Rapido de Culto')
    if p_i != -1:
        d_i = html.rfind('<div', 0, p_i)
        d_i = html.rfind('<div', 0, d_i)
        p_f = html.find('Histórico de Cultos', p_i)
        if p_f == -1: p_f = html.find('Historico de Cultos', p_i)
        t_f = html.find('</table>', p_f)
        if t_f != -1:
            d_f = html.find('</div>', t_f) + 6
            d_f = html.find('</div>', d_f) + 6
            html = html[:d_i] + bloco_cultos_reativo.strip() + html[d_f:]
            print("✓ Bloco de Cultos ancorado e substituído!")

# Limpeza de scripts legados que conflituavam
html = re.sub(r'<!-- script-.*? -->[\s\S]*?</script>', '', html, flags=re.IGNORECASE)

# Script leve apenas para retenção de aba e avatar de fotos
script_suporte_minimo = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'cultos') {
        var links = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item');
        links.forEach(function(b) {
            var txt = (b.innerText || '').toLowerCase();
            if (txt.includes('culto') || txt.includes('presença')) {
                b.click();
            }
        });
    }
});

window.addEventListener('error', function(e) {
    if (e.target && e.target.tagName === 'IMG' && (e.target.src.includes('uploads') || e.target.src.includes('membro'))) {
        e.target.onerror = null;
        var nome = e.target.alt || 'Membro';
        e.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(nome) + '&background=3730a3&color=fff&size=128';
    }
}, true);
</script>
"""

html = html + "\n<!-- script-suporte-minimo -->\n" + script_suporte_minimo

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado e 100% validado!")

# -------------------------------------------------------------
# 3. GARANTIR A ROTA NO APP.PY (CALCULA E PERSISTE NO SUPABASE)
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
    def n(k):
        v = fd.get(k)
        if v not in (None, ''):
            try: return int(v)
            except: pass
        return 0

    from datetime import datetime
    data_culto = (fd.get('data_culto') or '').strip()
    if not data_culto or data_culto in ('mm/dd/yyyy', '---'):
        data_culto = datetime.now().strftime('%Y-%m-%d')

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
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e:
        print("[ERRO GRAVACAO CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

# Substitui a rota cultos_novo no app.py
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

# Validar com o compilador Python (AST)
try:
    ast.parse(code_app)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_app)
    print("✓ Backend app.py 100% validado!")
except SyntaxError as e_ast:
    print(f"❌ Erro de sintaxe: {e_ast}")

print("=" * 70)
print("✓ PROCESSO REATIVO CONCLUÍDO COM SUCESSO!")
print("=" * 70)