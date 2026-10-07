import os
import re

pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Função para injetar as tags que forçam o envio e permitem fotos
                def consertar_form(match):
                    tag = match.group(0)
                    # 1. Força o envio ignorando bloqueios silenciosos (novalidate)
                    if 'novalidate' not in tag.lower():
                        tag = tag.replace('<form', '<form novalidate')
                    # 2. Permite o upload da foto para o servidor
                    if 'enctype' not in tag.lower() and 'post' in tag.lower():
                        tag = tag.replace('<form', '<form enctype="multipart/form-data"')
                    return tag

                padrao_form = r'(?i)<form[^>]*>'
                novo_conteudo = re.sub(padrao_form, consertar_form, conteudo)
                
                if novo_conteudo != conteudo:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(novo_conteudo)
                    print(f"✓ Formulário desbloqueado (Foto + Envio) no ficheiro: {file}")

    print("✓ Todos os formulários foram blindados com sucesso!")
else:
    print("Erro: Pasta 'templates' não encontrada.")