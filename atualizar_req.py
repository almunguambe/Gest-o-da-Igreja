with open('requirements.txt', 'r', encoding='utf-8') as f:
    linhas = [l.strip() for l in f.readlines() if l.strip()]

if not any('pg8000' in l for l in linhas):
    linhas.append('pg8000')

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(linhas) + '\n')

print("✓ pg8000 garantido no requirements.txt!")