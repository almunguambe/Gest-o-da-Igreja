import os
import ast
import re

print("=" * 60)
print("A LIMPAR O APP.PY E A COLOCAR O BOTÃO NO HTML...")
print("=" * 60)

# 1. LIMPAR O HTML MISTURADO DENTRO DO APP.PY
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove qualquer bloco de HTML que tenha caído dentro do app.py
padrao_html_solto = r'<!--[\s\S]*?-->|<a\s+href=[\s\S]*?</a>'
code_limpo = re.sub(padrao_html_solto, '', code)

# Validação imediata com o compilador Python (AST)
try:
    ast.parse(code_limpo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_limpo)
    print("✓ app.py limpo e validado com sucesso (sem erros de sintaxe)!")
except SyntaxError as e:
    print(f"Ajuste necessário na linha {e.lineno}: {e}")
    # Se ainda houver resíduos, remove linhas com caracteres HTML típicos
    linhas = [l for l in code_limpo.splitlines() if not any(tag in l for tag in ['<a ', '</a>', '<!--', '-->', 'class="btn-planificacao"'])]
    code_limpo = "\n".join(linhas)
    ast.parse(code_limpo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_limpo)
    print("✓ app.py recuperado e 100% aprovado pelo Python!")

# 2. INSERIR O BOTÃO NO TEMPLATE CORRETO (dashboard.html)
tpl_dash = os.path.join('templates', 'dashboard.html')
botao_html = """
<!-- ATALHO DE ACESSO À PLANIFICAÇÃO -->
<div style="margin: 20px 0; padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: space-between;">
    <div>
        <h4 style="margin: 0; color: #1e293b; font-size: 16px;">📌 Planificação de Actividades</h4>
        <p style="margin: 4px 0 0; color: #64748b; font-size: 13px;">Registo e monitoramento do cronograma dos departamentos.</p>
    </div>
    <a href="/secretaria/planificacao/nova" style="display: inline-flex; align-items: center; gap: 8px; background-color: #3730a3; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        Abrir Cronograma
    </a>
</div>
"""

if os.path.exists(tpl_dash):
    with open(tpl_dash, 'r', encoding='utf-8') as f:
        dash_content = f.read()

    if '/secretaria/planificacao/nova' not in dash_content:
        # Insere antes da tabela ou no início do container principal
        if '<div class="container' in dash_content:
            dash_content = dash_content.replace('<div class="container', botao_html + '\n<div class="container', 1)
        elif '<main' in dash_content:
            dash_content = dash_content.replace('<main', botao_html + '\n<main', 1)
        else:
            dash_content = botao_html + '\n' + dash_content

        with open(tpl_dash, 'w', encoding='utf-8') as f:
            f.write(dash_content)
        print("✓ Botão visual inserido corretamente em templates/dashboard.html!")
    else:
        print("O botão já está presente em templates/dashboard.html.")

print("=" * 60)
print("✓ TUDO CONCLUÍDO COM SUCESSO!")
print("=" * 60)