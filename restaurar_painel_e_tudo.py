import os
import subprocess
import re

print("=" * 65)
print("A RECUPERAR O DASHBOARD COMPLETO (SIDEBAR, MENUS E FOTOS)...")
print("=" * 65)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR O DASHBOARD ORIGINAL DO GIT (USANDO BARRA NORMAL /)
caminho_git = 'templates/dashboard.html'
res_log = subprocess.run(['git', 'log', '--format=%H', '-50'], capture_output=True, text=True)
commits = [c.strip() for c in res_log.stdout.strip().split('\n') if c.strip()]

conteudo_dashboard = None
commit_usado = None

for c in commits:
    try:
        # No Git tem de ser sempre / (POSIX) para não dar o erro do Windows
        texto = subprocess.check_output(['git', 'show', f'{c}:{caminho_git}'], text=True, encoding='utf-8')
        linhas = len(texto.splitlines())
        if linhas > 120:
            conteudo_dashboard = texto
            commit_usado = c
            print(f"✓ SUCESSO: Dashboard original recuperado do commit {c[:7]} com {linhas} linhas!")
            break
    except Exception:
        continue

if not conteudo_dashboard:
    print("A procurar nos backups locais...")
    if os.path.exists(tpl_dash + '.bak'):
        with open(tpl_dash + '.bak', 'r', encoding='utf-8', errors='ignore') as f:
            bak_txt = f.read()
            if len(bak_txt.splitlines()) > 100:
                conteudo_dashboard = bak_txt
                print("✓ Dashboard recuperado do ficheiro de backup local!")

if not conteudo_dashboard:
    print("ERRO: Não foi possível recuperar a versão longa. Verifique os ficheiros locais.")
    exit(1)

# 2. ADICIONAR O BOTÃO DA PLANIFICAÇÃO DENTRO DA SIDEBAR
item_sidebar = """
        <!-- Atalho Planificação Eclesiástica -->
        <a href="/secretaria/planificacao/nova" class="sidebar-item" style="display: flex; align-items: center; gap: 10px; padding: 10px 16px; color: #4338ca; background: #e0e7ff; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 8px 12px;">
            <span style="font-size: 18px;">📅</span>
            <span>Planificação & Cronograma</span>
        </a>
"""

if '/secretaria/planificacao/nova' not in conteudo_dashboard:
    # Insere antes do fecho da navegação ou no menu da secretaria
    if 'sidebar' in conteudo_dashboard.lower() or '<nav' in conteudo_dashboard.lower():
        match_nav = re.search(r'(</nav>|</ul>\s*</aside>|</div>\s*<!--\s*end\s*sidebar)', conteudo_dashboard, re.IGNORECASE)
        if match_nav:
            ponto = match_nav.start()
            conteudo_dashboard = conteudo_dashboard[:ponto] + item_sidebar + "\n" + conteudo_dashboard[ponto:]
        else:
            conteudo_dashboard = item_sidebar + "\n" + conteudo_dashboard
    else:
        conteudo_dashboard = item_sidebar + "\n" + conteudo_dashboard
    print("✓ Atalho de Planificação integrado na Sidebar!")

# 3. CORRIGIR FOTOS DOS MEMBROS (FALLBACK AUTOMÁTICO PARA AVATAR)
avatar_fallback = ' onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name=\' + encodeURIComponent(this.alt || \'Membro\') + \'&background=3730a3&color=fff&size=128\';" '

def aplicar_avatar(match):
    tag = match.group(0)
    if 'onerror' in tag:
        return tag
    return tag[:-1] + avatar_fallback + '>'

conteudo_dashboard = re.sub(r'<img[^>]+(?:foto|uploads|membro)[^>]*>', aplicar_avatar, conteudo_dashboard, flags=re.IGNORECASE)

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(conteudo_dashboard)
print("✓ templates/dashboard.html restaurado na íntegra com sidebar e fotos corrigidas!")

# 4. APLICAR PROTEÇÃO DE FOTOS EM TODOS OS OUTROS TEMPLATES
pasta_tpl = 'templates'
total_corrigidos = 0
for root, _, files in os.walk(pasta_tpl):
    for f in files:
        if f.endswith('.html') and f != 'dashboard.html':
            caminho = os.path.join(root, f)
            with open(caminho, 'r', encoding='utf-8', errors='ignore') as arq:
                html = arq.read()
            orig = html
            html = re.sub(r'<img[^>]+(?:foto|uploads|membro)[^>]*>', aplicar_avatar, html, flags=re.IGNORECASE)
            if orig != html:
                with open(caminho, 'w', encoding='utf-8') as arq:
                    arq.write(html)
                total_corrigidos += 1

print(f"✓ Proteção contra fotos quebradas aplicada em {total_corrigidos} ecrãs adicionais!")

# 5. GARANTIR QUE O BOTÃO "VOLTAR" ESTÁ NA TELA DE PLANIFICAÇÃO
for t in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
    caminho = os.path.join(pasta_tpl, t)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8', errors='ignore') as arq:
            txt = arq.read()
        if '← Voltar ao Painel' not in txt:
            barra_voltar = """
<div style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 12px 24px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <a href="/" style="display: inline-flex; align-items: center; gap: 8px; background: #f1f5f9; color: #1e293b; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; border: 1px solid #cbd5e1;">
        ← Voltar ao Painel Principal
    </a>
    <span style="color: #475569; font-size: 14px; font-weight: bold;">
        IEAD Chicuque • Secretaria & Gestão
    </span>
</div>
"""
            if '<body' in txt:
                txt = re.sub(r'(<body[^>]*>)', r'\1\n' + barra_voltar, txt, count=1)
            else:
                txt = barra_voltar + "\n" + txt
            with open(caminho, 'w', encoding='utf-8') as arq:
                arq.write(txt)
            print(f"✓ Botão de voltar ao painel instalado em {t}!")

print("=" * 65)
print("✓ PROCESSO COMPLETO REALIZADO COM SUCESSO!")
print("=" * 65)