import os
import re

# Localiza qual arquivo de relatório contém o texto do relatório
candidatos = [os.path.join('templates', f) for f in os.listdir('templates') if f.endswith('.html')]
alvo = None

for c in candidatos:
    with open(c, 'r', encoding='utf-8') as f:
        txt = f.read()
        if "RELATÓRIO ANUAL E ESTATÍSTICA" in txt or "Romão Semende" in txt or "Savanguane" in txt:
            alvo = c
            break

if not alvo:
    print("Arquivo específico não encontrado automaticamente, procurando em app.py...")
    alvo = 'templates/relatorio_anual.html' if os.path.exists('templates/relatorio_anual.html') else None

if alvo and os.path.exists(alvo):
    with open(alvo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Remover o nome de Romão e Savanguane
    conteudo = re.sub(r'Romão\s+Semende\s+Savanguane\s*(?://Evangelista//|\(Evangelista\))?', '', conteudo)

    # 2. Ajustar Título da Tabela 1
    conteudo = conteudo.replace("1. APRESENTAÇÃO DA ESTRUTURA DISTRITAL", "1. APRESENTAÇÃO DA LIDERANÇA DA IGREJA LOCAL")

    # 3. Ajustar as Funções para Igreja Local
    conteudo = conteudo.replace("Pastor Presidente / Coordenador", "Pastor da Igreja Local")
    conteudo = conteudo.replace("Pastor Distrital", "Pastor Local")
    conteudo = conteudo.replace("Secretário Distrital", "Secretário")
    conteudo = conteudo.replace("Tesoureiro Distrital", "Tesoureiro")

    # 4. Ajustar Assinaturas do Rodapé
    bloco_assinatura_antigo = r'<div[^>]*class="[^"]*flex[^"]*justify-between[^"]*".*?Visto do Pastor Presidente.*?O Secretário Distrital.*?</div>'
    
    novo_rodape_assinaturas = '''<div class="flex justify-between items-end mt-12 pt-6 text-xs font-bold text-slate-800">
        <div class="text-center w-64">
            <div class="border-b-2 border-slate-900 mb-2"></div>
            <span>O Pastor da Igreja Local</span>
        </div>
        <div class="text-center w-64">
            <div class="border-b-2 border-slate-900 mb-2"></div>
            <span>O Secretário</span>
        </div>
    </div>'''

    if "O Pastor da Igreja Local" not in conteudo:
        # Substitui menções no rodapé caso use divs simples
        conteudo = re.sub(r'Visto do Pastor Presidente / Coordenador', 'O Pastor da Igreja Local', conteudo)
        conteudo = re.sub(r'O Secretário Distrital', 'O Secretário', conteudo)

    with open(alvo, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print(f"✓ Arquivo {alvo} padronizado com sucesso para 'Pastor da Igreja Local' e 'Secretário' sem nomes fixos!")
else:
    print("! Por favor, indique o nome do arquivo HTML do relatório.")