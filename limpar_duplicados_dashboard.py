import re

with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localizar o início de render_template('dashboard.html'
inicio_tag = "return render_template('dashboard.html',"
pos_inicio = conteudo.find(inicio_tag)

if pos_inicio != -1:
    # Encontrar o fecho correspondente do render_template
    nivel_parenteses = 0
    pos_fim = -1
    for i in range(pos_inicio + len("return render_template"), len(conteudo)):
        if conteudo[i] == '(':
            nivel_parenteses += 1
        elif conteudo[i] == ')':
            nivel_parenteses -= 1
            if nivel_parenteses == 0:
                pos_fim = i + 1
                break

    if pos_fim != -1:
        bloco_completo = conteudo[pos_inicio:pos_fim]
        # Extrair tudo o que está dentro de render_template(...)
        conteudo_args = bloco_completo[len("return render_template("):-1]
        
        # Separar os argumentos por linhas/vírgulas
        linhas = conteudo_args.split("\n")
        args_vistos = set()
        novas_linhas = ["    return render_template('dashboard.html',"]

        for l in linhas:
            linha_limpa = l.strip()
            # Ignorar o primeiro argumento que é o nome do template
            if not linha_limpa or "'dashboard.html'" in linha_limpa or '"dashboard.html"' in linha_limpa:
                continue

            # Verificar se tem atribuição chave=valor
            if "=" in linha_limpa:
                chave = linha_limpa.split("=")[0].strip()
                if chave not in args_vistos:
                    args_vistos.add(chave)
                    novas_linhas.append(f"                           {linha_limpa}")
            else:
                novas_linhas.append(f"                           {linha_limpa}")

        # Fechar o bloco com formatação correta
        bloco_reconstruido = "\n".join(novas_linhas)
        if not bloco_reconstruido.rstrip().endswith(")"):
            bloco_reconstruido = bloco_reconstruido.rstrip().rstrip(",") + "\n    )"

        conteudo = conteudo[:pos_inicio] + bloco_reconstruido + conteudo[pos_fim:]

        with open("app.py", "w", encoding="utf-8") as f:
            f.write(conteudo)

        print("✓ Todos os argumentos duplicados foram limpos e desduplicados com sucesso!")
else:
    print("Aviso: 'return render_template('dashboard.html',' não foi localizado textualmente.")