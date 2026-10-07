import os

ficheiro_exato = None
pasta = 'templates'

# 1. Procura o nome EXATO do ficheiro (com as maiúsculas/minúsculas reais)
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    if 'Gravar Planificação' in f.read():
                        ficheiro_exato = os.path.relpath(caminho, pasta).replace('\\', '/')
                        break
        if ficheiro_exato:
            break

if ficheiro_exato:
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 2. Corrige o erro 500 do Linux ensinando-lhe o nome exato
    code = code.replace("render_template('nova_planificacao.html')", f"render_template('{ficheiro_exato}')")
    
    # 3. Garante que, ao gravar, a página recarrega para o sítio exato de onde veio
    code = code.replace("redirect('/secretaria/planificacao/nova')", "redirect(request.referrer or '/')")
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
        
    print(f"✓ Resolvido! O nome exato do seu ficheiro é: {ficheiro_exato}")
    print("✓ O app.py foi atualizado para não falhar no Render.")
else:
    print("Erro: Não encontrei o formulário.")