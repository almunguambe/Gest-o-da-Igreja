with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Substitui 'Membro em Prova' por 'Candidato ao Batismo'
antigo = '<option value="Membro em Prova">Membro em Prova</option>'
novo = '<option value="Candidato ao Batismo">Candidato ao Batismo</option>'

if antigo in conteudo:
    conteudo = conteudo.replace(antigo, novo)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Opção atualizada com sucesso para 'Candidato ao Batismo'!")
else:
    print("⚠️ Trecho exato não encontrado. Verifique as linhas próximas.")