with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

alvo_erro = 'print("Erro ao gravar planificacao:", e)'
novo_erro = 'return f"<h1>ERRO NO SUPABASE:</h1><p>{e}</p> <br><a href=\'/secretaria/planificacao/nova\'>Voltar</a>"'

alvo_sucesso = "return redirect(url_for('dashboard'))"
novo_sucesso = 'return f"<h1>SUCESSO! O Botão funciona!</h1><p>O Python leu os seguintes dados do formulário HTML:<br>Departamento: {departamento}<br>Actividade: {nome_actividade}</p><br><a href=\'/secretaria/planificacao/nova\'>Voltar</a>"'

if alvo_erro in code:
    code = code.replace(alvo_erro, novo_erro)
    code = code.replace(alvo_sucesso, novo_sucesso)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Raio-X injetado no app.py com sucesso!")
else:
    print("O Raio-X já estava aplicado ou a rota não foi encontrada.")