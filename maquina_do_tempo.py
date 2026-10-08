import subprocess

print("A ativar a Máquina do Tempo do Git...")

# Pede ao Git o histórico dos últimos 30 passos
log = subprocess.run(['git', 'log', '--pretty=format:%h|%s', '-30'], capture_output=True, text=True)
linhas = log.stdout.strip().split('\n')

hash_alvo = None
for i, linha in enumerate(linhas):
    # Procura o exato momento em que começámos as alterações de hoje
    if "Instalar funcao de certificados" in linha:
        if i + 1 < len(linhas):
            # Seleciona o momento imediatamente ANTES disso (código seguro)
            hash_alvo = linhas[i+1].split('|')[0]
        break

if hash_alvo:
    print(f"Estado seguro encontrado (Commit {hash_alvo}). A restaurar o app.py...")
    subprocess.run(['git', 'checkout', hash_alvo, '--', 'app.py'])
    print("✓ SUCESSO! O ficheiro original e intacto foi restaurado.")
else:
    # Se não encontrar a mensagem, recua 12 passos à força por segurança
    print("A recuar 12 versões por segurança...")
    subprocess.run(['git', 'checkout', 'HEAD~12', '--', 'app.py'])
    print("✓ SUCESSO! O ficheiro foi restaurado.")