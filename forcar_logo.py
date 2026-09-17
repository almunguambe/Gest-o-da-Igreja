import os

# 1. Atualizar templates/login.html para quebrar cache e exibir o emblema
login_path = os.path.join("templates", "login.html")
if os.path.exists(login_path):
    with open(login_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    # Atualiza a tag img adicionando parâmetro de versão contra cache
    conteudo = conteudo.replace('/static/logo.png', '/static/logo.png?v=2026')
    with open(login_path, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✓ Cache renovada no login.html!")

# 2. Atualizar templates/dashboard.html
dash_path = os.path.join("templates", "dashboard.html")
if os.path.exists(dash_path):
    with open(dash_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo = conteudo.replace('/static/logo.png', '/static/logo.png?v=2026')
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✓ Cache renovada no dashboard.html!")