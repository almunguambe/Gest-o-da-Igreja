with open("app.py", "r", encoding="utf-8") as f:
    linhas = f.readlines()

linhas_limpas = []
for i, l in enumerate(linhas):
    num = i + 1
    # Se estiver na região do erro (linhas 530 a 560)
    if 530 <= num <= 560:
        texto = l.strip()
        if texto.startswith("try:") or texto.startswith("except"):
            l = "    " + texto + "\n"
        elif texto.startswith("c.execute") or texto.startswith("duvidas_lista =") or texto.startswith("candidatos_discipulado =") or texto.startswith("pass"):
            l = "        " + texto + "\n"
        elif texto.startswith("conn.close()") or texto.startswith("alerta_duplicado =") or texto.startswith("sucesso_cadastro =") or texto.startswith("return render_template"):
            l = "    " + texto + "\n"
    linhas_limpas.append(l)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(linhas_limpas)

print("Ajuste concluído! Testando compilação...")