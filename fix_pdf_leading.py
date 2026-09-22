with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Corrigir o erro do <font ... leading=22> no gerador de cartas/certificados
# O atributo leading deve pertencer à tag <para> ou ao estilo do ReportLab
trecho_errado = "<font color='#1e293b' size=13 leading=22>"
trecho_correto = "<para leading=22><font color='#1e293b' size=13>"

if trecho_errado in conteudo:
    conteudo = conteudo.replace(trecho_errado, trecho_correto)
    # Se a tag fechar </font></para>, ajustamos se necessário
    print("✓ Sintaxe do ReportLab <font leading=...> corrigida com sucesso!")
else:
    # Substituição genérica para qualquer leading dentro de <font
    import re
    novo_conteudo = re.sub(r"<font\s+([^>]*?)leading=(\d+)([^>]*?)>", r"<para leading=\2><font \1\3>", conteudo)
    if novo_conteudo != conteudo:
        conteudo = novo_conteudo
        print("✓ Sintaxe do ReportLab ajustada via expressão regular!")
    else:
        print("! Padrão direto não encontrado, verificando ocorrências de 'leading'...")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)