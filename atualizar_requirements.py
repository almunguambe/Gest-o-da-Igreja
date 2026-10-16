import os

req_file = 'requirements.txt'
conteudo = ''
if os.path.exists(req_file):
    with open(req_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()

linhas = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]

# Garantir psycopg2-binary
if not any('psycopg2' in l for l in linhas):
    linhas.append('psycopg2-binary')
    print("  + psycopg2-binary adicionado ao requirements.txt")
else:
    # Substituir psycopg2 puro por psycopg2-binary caso esteja listado sem binary
    novas_linhas = []
    for l in linhas:
        if l == 'psycopg2':
            novas_linhas.append('psycopg2-binary')
            print("  + Atualizado psycopg2 para psycopg2-binary")
        else:
            novas_linhas.append(l)
    linhas = novas_linhas

with open(req_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(linhas) + '\n')

print("✓ requirements.txt verificado com sucesso:")
for l in linhas:
    print(f"  - {l}")")