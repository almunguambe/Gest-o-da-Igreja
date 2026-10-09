import os
import subprocess
import re
import ast

print("=" * 65)
print("A RESTAURAR O PAINEL PRINCIPAL (DASHBOARD) COM AS SIDEBARS...")
print("=" * 65)

tpl_dash = os.path.join('templates', 'dashboard.html')

# 1. FAZER BACKUP DO FICHEIRO ATUAL
if os.path.exists(tpl_dash):
    with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo_atual = f.read()
    with open(tpl_dash + '.bak', 'w', encoding='utf-8') as f:
        f.write(conteudo_atual)
    print(f"Linhas atuais no dashboard.html: {len(conteudo_atual.splitlines())}")

# 2. PROCURAR NO HISTÓRICO DO GIT O DASHBOARD COMPLETO (COM SIDEBAR)
cmd_commits = ['git', 'log', '--format=%H', '--', tpl_dash]
res = subprocess.run(cmd_commits, capture_output=True, text=True)
commits = [c.strip() for c in res.stdout.strip().split('\n') if c.strip()]

conteudo_restaurado = None
commit_encontrado = None

for c in commits:
    try:
        conteudo = subprocess.check_output(['git', 'show', f'{c}:{tpl_dash}'], text=True, encoding='utf-8')
        linhas = len(conteudo.splitlines())
        # O dashboard original tem muitas linhas e a estrutura do painel
        if linhas > 150 or ('sidebar' in conteudo.lower() and linhas > 80):
            conteudo_restaurado = conteudo
            commit_encontrado = c
            print(f"✓ Encontrado dashboard original no commit {c[:7]} com {linhas} linhas!")
            break
    except Exception:
        continue

# Se não encontrou no histórico específico, busca no histórico global do repositório
if not conteudo_restaurado:
    res_global = subprocess.run(['git', 'log', '--format=%H', '-30'], capture_output=True, text=True)
    commits_global = [c.strip() for c in res_global.stdout.strip().split('\n') if c.strip()]
    for c in commits_global:
        try:
            conteudo = subprocess.check_output(['git', 'show', f'{c}:{tpl_dash}'], text=True, encoding='utf-8')
            linhas = len(conteudo.splitlines())
            if linhas > 150 or ('sidebar' in conteudo.lower() and linhas > 80):
                conteudo_restaurado = conteudo
                commit_encontrado = c
                print(f"✓ Encontrado dashboard original no histórico geral ({c[:7]}) com {linhas} linhas!")
                break
        except Exception:
            continue

if not conteudo_restaurado:
    print("⚠️ Não foi possível localizar versão anterior no Git. A manter ficheiro existente.")
    conteudo_restaurado = conteudo_atual

# 3. COLOCAR O ATALHO DA PLANIFICAÇÃO DENTRO DA SIDEBAR
link_sidebar = """
        <!-- Atalho Planificação Eclesiástica -->
        <a href="/secretaria/planificacao/nova" class="sidebar-item" style="display: flex; align-items: center; gap: 10px; padding: 10px 15px; color: #4338ca; background: #e0e7ff; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 8px 10px;">
            <span>📅</span> Planificação & Cronograma
        </a>
"""

if '/secretaria/planificacao/nova' not in conteudo_restaurado:
    # Insere dentro da lista de navegação ou sidebar
    if 'sidebar' in conteudo_restaurado.lower():
        # Procura fecho do primeiro bloco de links da sidebar
        pos_nav = re.search(r'(</nav>|</div>\s*<!--\s*end\s*sidebar)', conteudo_restaurado, re.IGNORECASE)
        if pos_nav:
            idx = pos_nav.start()
            conteudo_restaurado = conteudo_restaurado[:idx] + link_sidebar + "\n" + conteudo_restaurado[idx:]
        else:
            conteudo_restaurado = link_sidebar + "\n" + conteudo_restaurado
    else:
        conteudo_restaurado = link_sidebar + "\n" + conteudo_restaurado
    print("✓ Atalho de Planificação integrado na barra de navegação/sidebar!")

# 4. RESOLVER AS FOTOS DOS MEMBROS COM AVATAR ELEGANTE (SEM ERRO 404)
avatar_fallback = ' onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name=\' + encodeURIComponent(this.alt || \'Membro\') + \'&background=3730a3&color=fff&size=128\';" '

def adicionar_onerror(match):
    tag = match.group(0)
    if 'onerror' in tag:
        return tag
    return tag[:-1] + avatar_fallback + '>'

conteudo_restaurado = re.sub(r'<img[^>]+(?:foto|uploads|membro)[^>]*>', adicionar_onerror, conteudo_restaurado, flags=re.IGNORECASE)

# Gravar o dashboard completo recuperado
with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(conteudo_restaurado)
print("✓ templates/dashboard.html restaurado e atualizado com sucesso!")

# 5. GARANTIR QUE AS FOTOS NOS OUTROS TEMPLATES TAMBÉM NÃO QUEBRAM
pasta_tpl = 'templates'
if os.path.exists(pasta_tpl):
    for root, _, files in os.walk(pasta_tpl):
        for f in files:
            if f.endswith('.html') and f != 'dashboard.html':
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as arq:
                    html_tpl = arq.read()
                orig_tpl = html_tpl
                html_tpl = re.sub(r'<img[^>]+(?:foto|uploads|membro)[^>]*>', adicionar_onerror, html_tpl, flags=re.IGNORECASE)
                if orig_tpl != html_tpl:
                    with open(p, 'w', encoding='utf-8') as arq:
                        arq.write(html_tpl)

print("✓ Proteção visual contra fotos quebradas ativada em todos os ecrãs!")

# 6. INVESTIGAÇÃO DO BOTÃO DO CERTIFICADO DA 1ª CLASSE
print("\n" + "=" * 65)
print("DIAGNÓSTICO DO CERTIFICADO DA 1ª CLASSE:")
print("=" * 65)

certificados_encontrados = []
for root, _, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as arq:
                for num, l in enumerate(arq, 1):
                    if any(t in l.lower() for t in ['certificado', 'c1_ok', 'emitir', 'gerar_certificado']):
                        certificados_encontrados.append((f, num, l.strip()))

with open('app.py', 'r', encoding='utf-8', errors='ignore') as arq:
    for num, l in enumerate(arq, 1):
        if any(t in l.lower() for t in ['certificado', 'c1_ok', 'emitir_certificado']):
            certificados_encontrados.append(('app.py', num, l.strip()))

if certificados_encontrados:
    for arq, num, l in certificados_encontrados[:8]:
        print(f"-> [{arq} : Linha {num}] {l[:90]}")
else:
    print("Nenhuma referência ao botão de certificado encontrada.")

print("=" * 65)
print("✓ PROCESSO DE RESTAURAÇÃO CONCLUÍDO!")
print("=" * 65)