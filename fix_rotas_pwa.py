with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

rotas_pwa = '''
@app.route('/manifest.json')
def serve_manifest():
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
def serve_sw():
    from flask import send_from_directory
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')
'''

if "def serve_manifest():" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", rotas_pwa + "\nif __name__ ==")
    else:
        conteudo += "\n" + rotas_pwa

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Rotas do PWA adicionadas com sucesso ao app.py!")