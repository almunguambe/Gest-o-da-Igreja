import os
import re

print("=" * 65)
print("INICIANDO AJUSTES: NAVEGAÇÃO, FOTOS E CERTIFICADO...")
print("=" * 65)

# -------------------------------------------------------------
# 1. BOTÃO "VOLTAR AO PAINEL" NA TELA DE PLANIFICAÇÃO
# -------------------------------------------------------------
pasta_tpl = 'templates'
barra_navegacao = """
<div style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 12px 24px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <a href="/" style="display: inline-flex; align-items: center; gap: 8px; background: #f1f5f9; color: #1e293b; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; border: 1px solid #cbd5e1;">
        ← Voltar ao Painel Principal
    </a>
    <span style="color: #475569; font-size: 14px; font-weight: bold;">
        IEAD Chicuque • Secretaria & Gestão
    </span>
</div>
"""

for tpl in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
    caminho = os.path.join(pasta_tpl, tpl)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        if '← Voltar ao Painel Principal' not in conteudo:
            # Insere logo no topo do corpo
            if '<body' in conteudo:
                conteudo = re.sub(r'(<body[^>]*>)', r'\1\n' + barra_navegacao, conteudo, count=1)
            else:
                conteudo = barra_navegacao + "\n" + conteudo
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"✓ Botão de voltar instalado com sucesso em {tpl}!")

# -------------------------------------------------------------
# 2. ATALHO DA PLANIFICAÇÃO NO PAINEL PRINCIPAL (dashboard.html)
# -------------------------------------------------------------
tpl_dash = os.path.join(pasta_tpl, 'dashboard.html')
if os.path.exists(tpl_dash):
    with open(tpl_dash, 'r', encoding='utf-8') as f:
        dash = f.read()

    botao_atalho = """
<!-- ATALHO PARA PLANIFICAÇÃO -->
<div style="margin: 15px 0; padding: 12px 18px; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 20px;">📅</span>
        <strong style="color: #3730a3;">Cronograma Eclesiástico da Secretaria</strong>
    </div>
    <a href="/secretaria/planificacao/nova" style="background: #3730a3; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px;">
        Abrir Planificação →
    </a>
</div>
"""
    if '/secretaria/planificacao/nova' not in dash:
        if '<div class="container' in dash:
            dash = dash.replace('<div class="container', botao_atalho + '\n<div class="container', 1)
        elif '<main' in dash:
            dash = dash.replace('<main', botao_atalho + '\n<main', 1)
        else:
            dash = botao_atalho + "\n" + dash
        with open(tpl_dash, 'w', encoding='utf-8') as f:
            f.write(dash)
        print("✓ Atalho para planificação adicionado no dashboard.html!")

# -------------------------------------------------------------
# 3. CORRIGIR FOTOS DOS MEMBROS COM AVATAR ELEGANTE (SEM ERROS 404)
# -------------------------------------------------------------
avatar_fallback = ' onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name=\' + encodeURIComponent(this.alt || \'Membro\') + \'&background=3730a3&color=fff&size=128\';" '

arquivos_atualizados = 0
if os.path.exists(pasta_tpl):
    for root, _, files in os.walk(pasta_tpl):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as arq:
                    html = arq.read()
                
                original = html
                # Adiciona fallback a todas as tags de imagem de membros que não tenham onerror
                def substituir_img(match):
                    tag = match.group(0)
                    if 'onerror' in tag:
                        return tag
                    return tag[:-1] + avatar_fallback + '>'

                html = re.sub(r'<img[^>]+(?:foto|uploads|membro)[^>]*>', substituir_img, html, flags=re.IGNORECASE)
                
                if original != html:
                    with open(p, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    arquivos_atualizados += 1

print(f"✓ Proteção contra fotos quebradas aplicada em {arquivos_atualizados} ecrãs!")

# -------------------------------------------------------------
# 4. INVESTIGAÇÃO DO BOTÃO DO CERTIFICADO DA 1ª CLASSE
# -------------------------------------------------------------
print("\n" + "="*65)
print("RELATÓRIO DO BOTÃO DO CERTIFICADO (CLASSE 1 / DISCIPULADO):")
print("="*65)

encontrados = []
for root, _, files in os.walk(pasta_tpl):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as arq:
                linhas = arq.readlines()
            for num, l in enumerate(linhas, 1):
                if any(termo in l.lower() for termo in ['certificado', 'c1_ok', 'emitir', 'gerar_certificado']):
                    encontrados.append((f, num, l.strip()))

if encontrados:
    for f, num, l in encontrados[:10]:
        print(f"- [{f} Linha {num}]: {l[:90]}")
else:
    print("Nenhuma referência a 'certificado' encontrada nos templates HTML.")

print("=" * 65)
print("✓ AJUSTES CONCLUÍDOS COM SUCESSO!")
print("=" * 65)