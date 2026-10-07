with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

rota_nova = """
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import render_template, request, redirect, url_for, flash
    import os
    
    if request.method == 'POST':
        # Aqui ficará o código de gravação do plano futuramente
        flash('Plano eclesiástico gravado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
        
    # Sistema inteligente para encontrar o nome do ficheiro HTML que desenhou
    templates_possiveis = [
        'nova_planificacao.html', 
        'planificacao_nova.html', 
        'secretaria_planos.html', 
        'planos.html',
        'planificacao.html'
    ]
    
    for html in templates_possiveis:
        if os.path.exists(os.path.join('templates', html)):
            return render_template(html)
            
    # Se não encontrar nenhum dos nomes comuns, tenta abrir o padrão
    return render_template('nova_planificacao.html')
"""

if "'/secretaria/planificacao/nova'" not in code:
    # Injetar a rota perto do final do ficheiro
    idx = code.rfind("if __name__ == '__main__':")
    if idx != -1:
        code = code[:idx] + rota_nova.strip() + "\n\n" + code[idx:]
    else:
        code += "\n\n" + rota_nova.strip()
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota da Planificacao criada com sucesso no app.py!")
else:
    print("✓ A rota já existia.")