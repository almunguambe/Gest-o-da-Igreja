with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. Garantir que flash esteja no import de flask
if 'from flask import' in codigo:
    linhas = codigo.splitlines()
    for idx, l in enumerate(linhas):
        if 'from flask import' in l and 'flash' not in l:
            linhas[idx] = l.replace('from flask import ', 'from flask import flash, ')
            break
    codigo = "\n".join(linhas)

# 2. Corrigir o redirecionamento na função atualizar_fase_discipulado
antigo_retorno = "return redirect(url_for('dashboard') + \"#secao-discipulado\")"
novo_retorno = "return redirect('/#secao-discipulado')"

if antigo_retorno in codigo:
    codigo = codigo.replace(antigo_retorno, novo_retorno)

# Também assegurar outros redirects para dashboard que possam falhar caso a função se chame 'index'
codigo = codigo.replace("return redirect(url_for('dashboard'))", "return redirect('/')")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(codigo)

print("✓ Imports e redirecionamentos corrigidos com sucesso!")