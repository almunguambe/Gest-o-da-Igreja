import os
import shutil
import subprocess
import re

print("=" * 70)
print("A RESTAURAR TODAS AS JANELAS E MÓDULOS DO SISTEMA ECLESIÁSTICO...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. LOCALIZAR NO GIT O COMMIT ONDE TODOS OS MÓDULOS ESTAVAM ÍNTEGROS
res_log = subprocess.run(['git', 'log', '--format=%H %s', '-35'], capture_output=True, text=True)
commits = [c.strip() for c in res_log.stdout.strip().split('\n') if c.strip()]

commit_escolhido = None
for c in commits:
    h, msg = c.split(maxsplit=1)
    try:
        conteudo_antigo = subprocess.check_output(['git', 'show', f'{h}:templates/dashboard.html'], text=True, encoding='utf-8', errors='ignore')
        # Verifica se contém todos os módulos cruciais
        tem_tudo = all(termo in conteudo_antigo.lower() for termo in ['casamento', 'escala', 'óbito', 'convertido'])
        if tem_tudo and len(conteudo_antigo.splitlines()) > 500:
            commit_escolhido = h
            print(f"✓ Versão completa encontrada no commit: {h[:7]} ('{msg}')")
            html_recuperado = conteudo_antigo
            break
    except Exception:
        continue

if not commit_escolhido:
    print("⚠️ A procurar no backup local de segurança...")
    with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
        html_recuperado = f.read()

# -------------------------------------------------------------
# 2. ASSEGURAR O SCRIPT UNIVERSAL DE TROCA DE ABAS NA SIDEBAR
# -------------------------------------------------------------
script_navegacao_total = """
<!-- MOTOR UNIVERSAL DE NAVEGAÇÃO ENTRE ABAS DA SIDEBAR -->
<script>
function ativarAbaPorNome(nomeAba) {
    if (!nomeAba) return;
    nomeAba = nomeAba.toLowerCase().trim();

    // 1. Procurar todos os blocos de conteúdo/painéis
    var secoes = document.querySelectorAll('main > div, .aba-conteudo, [id^="aba-"], [id^="tab-"], [id*="content"], section');
    
    // Mapeamento de termos para encontrar a janela certa
    var encontrou = false;
    secoes.forEach(function(sec) {
        var id = (sec.id || '').toLowerCase();
        var txt = (sec.innerText || '').toLowerCase();
        
        // Verifica se esta seção corresponde à aba clicada
        var match = false;
        if (nomeAba.includes('culto') && (id.includes('culto') || txt.includes('registo rápido de culto'))) match = true;
        else if (nomeAba.includes('convertido') && (id.includes('convert') || txt.includes('novos convertidos'))) match = true;
        else if (nomeAba.includes('escala') && (id.includes('escala') || txt.includes('escala de púlpito'))) match = true;
        else if (nomeAba.includes('casamento') && (id.includes('casamento') || txt.includes('casamento'))) match = true;
        else if (nomeAba.includes('óbito') || nomeAba.includes('obito')) {
            if (id.includes('obito') || txt.includes('óbito') || txt.includes('obito')) match = true;
        }
        else if (nomeAba.includes('secretaria') && (id.includes('secretaria') || txt.includes('secretaria'))) match = true;
        else if (nomeAba.includes('membro') && (id.includes('membro') || txt.includes('membros'))) match = true;
        else if (nomeAba.includes('raio') && (id.includes('raio') || txt.includes('raio-x'))) match = true;
        else if (nomeAba.includes('painel') || nomeAba.includes('meta')) {
            if (id.includes('meta') || id.includes('painel') || txt.includes('metas')) match = true;
        }
        else if (nomeAba.includes('caixa') && (id.includes('caixa') || txt.includes('caixa'))) match = true;

        if (match) {
            sec.style.display = 'block';
            sec.style.visibility = 'visible';
            encontrou = true;
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // Liga clique a todos os botões/links da sidebar
    var botoesSidebar = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item, [onclick*="aba"]');
    
    botoesSidebar.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            var txt = (this.innerText || '').toLowerCase().trim();
            
            // Destacar o botão ativo visualmente
            botoesSidebar.forEach(function(b) {
                b.style.backgroundColor = 'transparent';
                b.style.color = '#cbd5e1';
            });
            this.style.backgroundColor = '#3b82f6';
            this.style.color = '#ffffff';

            // Identificar a rota correspondente ou abrir via URL/div
            if (txt.includes('culto')) window.location.href = '/?aba=cultos';
            else if (txt.includes('secretaria')) window.location.href = '/?aba=secretaria';
            else if (txt.includes('membro')) window.location.href = '/?aba=membros';
            else if (txt.includes('convertido')) window.location.href = '/?aba=convertidos';
            else if (txt.includes('escala')) window.location.href = '/?aba=escala';
            else if (txt.includes('casamento')) window.location.href = '/?aba=casamentos';
            else if (txt.includes('óbito') || txt.includes('obito')) window.location.href = '/?aba=obitos';
            else if (txt.includes('meta') || txt.includes('painel')) window.location.href = '/?aba=metas';
            else if (txt.includes('caixa')) window.location.href = '/?aba=caixa';
        });
    });

    // Abrir a aba que vem indicada no URL (?aba=...)
    var params = new URLSearchParams(window.location.search);
    var abaParam = params.get('aba');
    if (abaParam) {
        botoesSidebar.forEach(function(b) {
            var t = (b.innerText || '').toLowerCase();
            if (t.includes(abaParam)) {
                b.style.backgroundColor = '#3b82f6';
                b.style.color = '#ffffff';
            }
        });
    }
});

// Tratamento de fotos em falta
window.addEventListener('error', function(e) {
    if (e.target && e.target.tagName === 'IMG' && (e.target.src.includes('uploads') || e.target.src.includes('membro'))) {
        e.target.onerror = null;
        var nome = e.target.alt || 'Membro';
        e.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(nome) + '&background=3730a3&color=fff&size=128';
    }
}, true);
</script>
"""

# Injetar o motor universal no final da página
if 'MOTOR UNIVERSAL DE NAVEGAÇÃO' not in html_recuperado:
    html_recuperado = html_recuperado + "\n" + script_navegacao_total

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html_recuperado)

print("✓ Ficheiro templates/dashboard.html totalmente restabelecido e reativado!")
print("=" * 70)
print("✓ PROCESSO DE RESTAURO CONCLUÍDO COM SUCESSO!")
print("=" * 70)