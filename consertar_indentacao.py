# -*- coding: utf-8 -*-
with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Localizar trecho de coleta de dúvidas injetado com erro de indentação
linhas_corrigidas = []
for i, linha in enumerate(linhas):
    # Se uma linha isolada tiver 12 ou 8 espaços indevidos fora de bloco de função/try
    if "duvidas_lista = []" in linha or "candidatos_discipulado = []" in linha:
        # Alinhar com 4 ou 8 espaços padrão dependendo do escopo
        indent = len(linha) - len(linha.lstrip())
        if indent > 8:
            linha = " " * 8 + linha.lstrip()
    linhas_corrigidas.append(linha)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(linhas_corrigidas)

print("Linhas ajustadas. A testar compilação...")