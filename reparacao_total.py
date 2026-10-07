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
                original = conteudo

                # 1. DESTRAVAR BOTÃO GRAVAR: Remove todos os atributos 'required' que bloqueiam o envio silenciosamente
                conteudo = re.sub(r'\brequired(="[^"]*")?', '', conteudo, flags=re.IGNORECASE)

                # 2. ZONAS ECLESIÁSTICAS: Injetar opções caso o select esteja vazio
                if 'name="zona_eclesiastica"' in conteudo and 'Sede Chicuque' not in conteudo:
                    conteudo = re.sub(
                        r'(<select[^>]*name=["\']zona_eclesiastica["\'][^>]*>)',
                        r'\1\n<option value="">-- Selecione a Zona --</option>\n<option value="Sede Chicuque">Sede Chicuque</option>\n<option value="Maxixe">Maxixe</option>\n<option value="Inhambane">Inhambane</option>',
                        conteudo, flags=re.IGNORECASE
                    )
                
                # 3. NATURALIDADE: Injetar opções caso esteja vazio
                if 'name="naturalidade"' in conteudo and 'Maputo' not in conteudo:
                    conteudo = re.sub(
                        r'(<select[^>]*name=["\']naturalidade["\'][^>]*>)',
                        r'\1\n<option value="">-- Selecione --</option>\n<option value="Inhambane">Inhambane</option>\n<option value="Maputo">Maputo</option>\n<option value="Gaza">Gaza</option>\n<option value="Sofala">Sofala</option>',
                        conteudo, flags=re.IGNORECASE
                    )

                # 4. AVATAR / IMAGENS: Substitui erros de foto por um avatar azul com iniciais
                conteudo = re.sub(r'onerror="[^"]*"', '', conteudo) # Limpa erros antigos
                padrao_img = r'(<img[^>]*membro\.foto[^>]*)>'
                substituicao_img = r'\1 onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name=Membro&background=0D8ABC&color=fff\';">'
                conteudo = re.sub(padrao_img, substituicao_img, conteudo)

                # Grava apenas se houver alterações
                if conteudo != original:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Reparado: {file}")
                    
    print("\n✓ Formulários destravados, selects preenchidos e imagens corrigidas!")
else:
    print("Erro: Pasta 'templates' não encontrada.")