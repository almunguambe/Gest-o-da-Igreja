with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# Localizar onde a rota index ('/') busca dados e injetar planos
if "planos = conn.execute(" not in conteudo:
    padrao = r"(conn\s*=\s*get_db\(\).*?)(return render_template\('dashboard\.html')"
    
    # Injetamos a query antes do return render_template
    def repl(m):
        bloco_db = m.group(1)
        retorno = m.group(2)
        injecao = """
    try:
        planos = conn.execute("SELECT * FROM actividades_planeamento ORDER BY id DESC").fetchall()
    except Exception:
        planos = []
    """
        return bloco_db + injecao + retorno

    conteudo = re.sub(padrao, repl, conteudo, count=1, flags=re.DOTALL)
    
    # E adicionar planos=planos dentro do render_template('dashboard.html', ...)
    conteudo = conteudo.replace("render_template('dashboard.html',", "render_template('dashboard.html', planos=planos,")
    print("✓ Variável planos injetada na rota index do app.py!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)