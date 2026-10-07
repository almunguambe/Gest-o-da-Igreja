with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir o manipulador genérico de erro 500 para imprimir a exceção completa na tela
bloco_erro = """
@app.errorhandler(500)
def handle_500(e):
    import traceback
    orig = getattr(e, 'original_exception', e)
    tb = traceback.format_exc()
    return f'''
    <div style="font-family: monospace; padding: 20px; background: #fff3f3; border: 2px solid #e74c3c;">
        <h2 style="color: #c0392b;">Erro 500 no Servidor</h2>
        <p><b>Exceção:</b> {orig}</p>
        <pre style="background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto;">{tb}</pre>
    </div>
    ''', 500
"""

if "@app.errorhandler(500)" in code:
    idx = code.find("@app.errorhandler(500)")
    fim = code.find("\n@app.", idx + 10)
    if fim == -1:
        fim = code.find("\ndef ", idx + 10)
    if fim != -1:
        code = code[:idx] + bloco_erro.strip() + "\n\n" + code[fim:]
    else:
        code = code[:idx] + bloco_erro.strip()
else:
    code += "\n\n" + bloco_erro.strip()

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Capturador de erros detalhado configurado!")