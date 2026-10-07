import os
import re

pasta_templates = 'templates'

if not os.path.exists(pasta_templates):
    print("Pasta 'templates' não encontrada! Certifique-se de que está na raiz do projeto.")
else:
    for root, dirs, files in os.walk(pasta_templates):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                alterado = False
                
                # 1. Corrigir o texto estático "Lição 6 de 8"
                if "Lição 6 de 8" in conteudo:
                    # Substitui pelo número genérico ou remove o texto fixo que não corresponde
                    conteudo = conteudo.replace("Lição 6 de 8", "Lição Atual")
                    alterado = True
                    print(f"✓ Texto da Lição corrigido no ficheiro: {file}")
                
                # 2. Corrigir a foto quebrada do membro inserindo as iniciais automáticas
                if "membro.foto" in conteudo and "onerror" not in conteudo:
                    # Encontra a tag <img ... membro.foto ...> e adiciona o onerror
                    padrao = r'(<img[^>]*src=[\'"][^\'"]*membro\.foto[^\'"]*[\'"][^>]*)>'
                    substituicao = r'\1 onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={{ membro.nome | urlencode }}&background=random&color=fff\';">'
                    novo_conteudo = re.sub(padrao, substituicao, conteudo)
                    
                    if novo_conteudo != conteudo:
                        conteudo = novo_conteudo
                        alterado = True
                        print(f"✓ Avatar com iniciais adicionado no ficheiro: {file}")
                
                # Gravar as alterações se algo foi modificado
                if alterado:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)

    print("✓ Varredura visual concluída com sucesso!")