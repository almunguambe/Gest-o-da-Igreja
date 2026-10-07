import os

termos = ['Membros Registados', 'Ficha de Membro', 'Baixar Excel', 'Raio-X Estatístico']
encontrados = []

for raiz, _, ficheiros in os.walk('.'):
    if '.git' in raiz or '__pycache__' in raiz or 'venv' in raiz:
        continue
    for f in ficheiros:
        if f.endswith('.html') or f.endswith('.py'):
            caminho = os.path.join(raiz, f)
            try:
                conteudo = open(caminho, 'r', encoding='utf-8', errors='ignore').read()
                termos_presentes = [t for t in termos if t in conteudo]
                if termos_presentes:
                    encontrados.append((caminho, termos_presentes))
            except Exception:
                pass

print("=== FICHEIROS IDENTIFICADOS ===")
for caminho, matches in encontrados:
    print(f"{caminho} -> {matches}")