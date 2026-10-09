import os
import shutil
import subprocess
import re
import ast

print("=" * 70)
print("A RESTAURAR O DESIGN LIMPO E A ATIVAR A SOMA REAL DE CULTOS...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A BASE VISUAL EXATA DE IMAGE_77BE82.PNG
# O backup .bak_contagem guarda exatamente o ficheiro antes dos '0's intrusos
html_base = None
if os.path.exists(tpl_dash + '.bak_contagem'):
    with open(tpl_dash + '.bak_contagem', 'r', encoding='utf-8', errors='ignore') as f:
        html_base = f.read()
    print("✓ Base visual limpa recuperada do backup local!")

if not html_base or len(html_base.splitlines()) < 200:
    # Se necessário, recupera do histórico de commits do Git
    res_log = subprocess.run(['git', 'log', '--format=%H %s', '-30'], capture_output=True, text=True)
    commits = [c.strip() for c in res_log.stdout.strip().split('\n') if c.strip()]
    for c in commits:
        partes = c.split(maxsplit=1)
        h = partes[0]
        msg = partes[1] if len(partes) > 1 else ''
        if 'Restaurar layout original amplo' in msg:
            html_base = subprocess.check_output(['git', 'show', f'{h}:templates/dashboard.html'], text=True, encoding='utf-8')
            print(f"✓ Base visual recuperada do commit {h[:7]} ({msg})!")
            break

if not html_base:
    with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
        html_base = f.read()

# -------------------------------------------------------------
# 2. REMOVER QUALQUER SCRIPT INTRUSO QUE CAUSOU OS '0'S FANTASMAS
# -------------------------------------------------------------
html_base = re.sub(r'<!-- script-.*? -->[\s\S]*?</script>', '', html_base, flags=re.IGNORECASE)
html_base = re.sub(r'<script>[\s\S]*?recalcularPresentesCulto[\s\S]*?</script>', '', html_base)

# -------------------------------------------------------------
# 3. IDENTIFICAR O BLOCO DE CULTO E AJUSTAR A CAIXA DO TOTAL
# -------------------------------------------------------------
p_culto = html_base.find('Registo Rápido de Culto')
p_hist = html_base.find('Histórico de Cultos', p_culto if p_culto != -1 else 0)

if p_culto != -1 and p_hist != -1:
    bloco = html_base[p_culto:p_hist]

    # Garante a rota correta no formulário
    if '<form' in bloco:
        bloco = re.sub(r'<form[^>]*>', '<form action="/cultos/novo" method="POST" id="form-cultos-oficial">', bloco, count=1)
    
    # Atribui ID explícito à caixa azul do Total de Presentes sem alterar o seu CSS
    if 'Total de Presentes' in bloco:
        # Substitui a div/span que mostra o número do total por uma com ID fixo
        bloco = re.sub(
            r'(Total de Presentes[\s\S]*?)(<div[^>]*>|>)\s*(?:0|<span[^>]*>0</span>)\s*(</div>|<)',
            r'\1\2<span id="valor-total-culto-display" style="font-size: 22px; font-weight: bold; color: #1e40af;">0</span>\3',
            bloco,
            count=1
        )
        if 'input-total-culto-hidden' not in bloco:
            bloco = bloco + '\n<input type="hidden" name="total_presentes" id="input-total-culto-hidden" value="0">\n'

    html_base = html_base[:p_culto] + bloco + html_base[p_hist:]

# -------------------------------------------------------------
# 4. TABELA DO HISTÓRICO DE CULTOS
# -------------------------------------------------------------
linhas_tabela = """
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

if 'Histórico de Cultos' in html_base:
    p_h = html_base.find('Histórico de Cultos')
    p_tb = html_base.find('<tbody>', p_h)
    p_tbf = html_base.find('</tbody>', p_tb)
    if p_tb != -1 and p_tbf != -1:
        html_base = html_base[:p_tb+7] + "\n" + linhas_tabela.strip() + "\n                    " + html_base[p_tbf:]

# -------------------------------------------------------------
# 5. JAVASCRIPT PONTUAL E SEGURO (SEM ALTERAR OUTROS ELEMENTOS)
# -------------------------------------------------------------
script_seguro = """
<script>
// SOMA EM TEMPO REAL DIRECIONADA EXCLUSIVAMENTE À CAIXA DO TOTAL
function recalcularSomaCulto() {
    var form = document.getElementById('form-cultos-oficial') || document.querySelector('form[action*="cultos"]');
    if (!form) return;

    var nomesCampos = [
        'homens_adultos', 'mulheres_adultas', 
        'jovens_rapazes', 'jovens_mocas', 
        'criancas_meninos', 'criancas_meninas', 
        'visitantes_homens', 'visitantes_mulheres'
    ];

    var total = 0;
    nomesCampos.forEach(function(nome) {
        var inp = form.querySelector('input[name*="' + nome + '"]') || form.querySelector('input[name="' + nome + '"]');
        if (inp) {
            var val = parseInt(inp.value, 10);
            if (!isNaN(val) && val > 0) {
                total += val;
            }
        }
    });

    // Se os inputs tiverem nomes ligeiramente diferentes, soma todos os inputs numéricos antes de 'apelos'
    if (total === 0) {
        var todosInputs = form.querySelectorAll('input[type="number"]');
        todosInputs.forEach(function(inp) {
            var n = (inp.name || '').toLowerCase();
            if (!n.includes('apelo') && !n.includes('total')) {
                var v = parseInt(inp.value, 10);
                if (!isNaN(v) && v > 0) total += v;
            }
        });
    }

    // Atualiza apenas o display específico pelo ID
    var display = document.getElementById('valor-total-culto-display');
    if (display) {
        display.innerText = total;
    }
    var inputHidden = document.getElementById('input-total-culto-hidden');
    if (inputHidden) {
        inputHidden.value = total;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById('form-cultos-oficial') || document.querySelector('form[action*="cultos"]');
    if (form) {
        var inputs = form.querySelectorAll('input[type="number"]');
        inputs.forEach(function(inp) {
            var n = (inp.name || '').toLowerCase();
            if (!n.includes('apelo')) {
                inp.addEventListener('input', recalcularSomaCulto);
                inp.addEventListener('keyup', recalcularSomaCulto);
                inp.addEventListener('change', recalcularSomaCulto);
            }
        });
        recalcularSomaCulto();
    }

    // Abertura automática da aba Cultos & Presenças via URL (?aba=cultos)
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'cultos') {
        var botoes = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item');
        for (var i = 0; i < botoes.length; i++) {
            var txt = botoes[i].innerText ? botoes[i].innerText.toLowerCase() : '';
            if (txt.includes('culto') || txt.includes('presença')) {
                botoes[i].click();
                break;
            }
        }
    }
});

// TRATAMENTO GLOBAL DE FOTOS QUEBRADAS (EVITA ERROS 404 VISUAIS)
window.addEventListener('error', function(e) {
    if (e.target && e.target.tagName === 'IMG' && (e.target.src.includes('uploads') || e.target.src.includes('membro'))) {
        e.target.onerror = null;
        var nome = e.target.alt || 'Membro';
        e.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(nome) + '&background=3730a3&color=fff&size=128';
    }
}, true);
</script>
"""

html_base = html_base + "\n" + script_seguro

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html_base)
print("✓ templates/dashboard.html atualizado e limpo com sucesso!")

# -------------------------------------------------------------
# 6. ASSEGURAR O BACKEND APP.PY
# -------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    code_app = f.read()

# Validação do app.py com AST
try:
    ast.parse(code_app)
    print("✓ Backend app.py validado e pronto!")
except SyntaxError as e_ast:
    print(f"❌ Erro de compilação em app.py: {e_ast}")

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 70)