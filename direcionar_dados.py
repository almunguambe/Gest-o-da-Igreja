import os

pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Injeta a morada exata no motor JavaScript
                if 'form.method = "POST";' in conteudo and 'form.action' not in conteudo:
                    conteudo = conteudo.replace(
                        'form.method = "POST";', 
                        'form.method = "POST";\n            form.action = "/secretaria/planificacao/nova";'
                    )
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Morada de destino corrigida no ficheiro: {file}")

print("✓ O Motor agora sabe para onde enviar os dados!")