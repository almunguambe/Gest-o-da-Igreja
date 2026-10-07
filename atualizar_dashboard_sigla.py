with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Atualiza títulos institucionais do dashboard
html = html.replace("<title>IEAD Chicuque - Gestão & Ensino</title>", "<title>SIGAD • Sistema Integrado de Gestão Eclesiástica</title>")
html = html.replace("IEAD Chicuque - Gestão & Ensino", "SIGAD • Assembleia de Deus")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ SIGAD aplicado no dashboard com sucesso!")