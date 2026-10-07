with open('app.py', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

modificado = False
for i in range(len(linhas)):
    if 'Pastor Presidente' in linhas[i] and 'drawRightString' in linhas[i]:
        linhas[i] = '    c.drawCentredString(4.5*cm, 0.4*cm, "Pastor Presidente")\n'
        modificado = True
    elif 'line(5.5*cm, 0.65*cm, 8.0*cm, 0.65*cm)' in linhas[i]:
        linhas[i] = '    c.line(2.8*cm, 0.65*cm, 6.2*cm, 0.65*cm)\n'
        modificado = True

if modificado:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✓ Assinatura do Pastor Presidente reposicionada com sucesso!")
else:
    print("! Linhas não encontradas para substituição.")