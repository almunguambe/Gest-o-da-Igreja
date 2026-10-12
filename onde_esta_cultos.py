import os

print("=" * 70)
print("A INVESTIGAR ONDE ESTÁ LOCALIZADO O MÓDULO DE CULTOS...")
print("=" * 70)

termos = ['registo rápido de culto', 'registo rapido de culto', 'histórico de cultos', 'historico de cultos']
encontrados = []

for root, _, files in os.walk('.'):
    # Ignora pastas de ambiente virtual e git
    if any(ign in root for ign in ['.git', '.venv', 'venv', '__pycache__']):
        continue
    for f in files:
        if f.endswith(('.html', '.py', '.js')):
            caminho = os.path.join(root, f)
            try:
                with open(caminho, 'r', encoding='utf-8', errors='ignore') as arq:
                    linhas = arq.readlines()
                    for num, l in enumerate(linhas, 1):
                        l_low = l.lower()
                        for t in termos:
                            if t in l_low:
                                encontrados.append((caminho, num, l.strip()))
            except Exception:
                pass

if encontrados:
    print(f"✓ Encontradas {len(encontrados)} referências:")
    ficheiros_unicos = set()
    for caminho, num, linha in encontrados:
        ficheiros_unicos.add(caminho)
        print(f" -> [{caminho} : Linha {num}] {linha[:80]}")
    
    print("\nFicheiros que contêm o módulo de cultos:")
    for f in ficheiros_unicos:
        print(f" => {f}")
else:
    print("❌ Nenhuma ocorrência de 'Registo Rápido de Culto' encontrada nos ficheiros!")

print("=" * 70)