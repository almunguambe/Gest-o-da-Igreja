with open("app.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Fixar o numero do admin 866677810 (258866677810) na rota /estudos
antigo_bloco = """    # Busca o contacto do Pastor registado nos membros
    conn = get_db()
    pastor = conn.execute("SELECT telefone FROM membros WHERE posicao_atual LIKE '%Pastor%' AND telefone IS NOT NULL AND telefone != '' ORDER BY id ASC LIMIT 1").fetchone()
    conn.close()
    
    tel_pastor = ""
    if pastor and pastor['telefone']:
        tel_pastor = ''.join(filter(str.isdigit, str(pastor['telefone'])))
        if not tel_pastor.startswith("258"):
            tel_pastor = "258" + tel_pastor[-9:]
            
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_pastor)"""

novo_bloco = """    # Contacto oficial de gestao e apoio aos candidatos (Admin IEAD Chicuque)
    tel_admin = "258866677810"
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_admin)"""

if antigo_bloco in codigo:
    codigo = codigo.replace(antigo_bloco, novo_bloco)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(codigo)
    print("✓ app.py configurado com o número oficial do Admin: 258866677810!")
else:
    # Caso a rota esteja no formato original sem o bloco anterior
    codigo = codigo.replace(
        "return render_template('estudos.html', resultado_teste=resultado_teste)",
        'return render_template(\'estudos.html\', resultado_teste=resultado_teste, tel_pastor="258866677810")'
    )
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(codigo)
    print("✓ app.py atualizado com o número 258866677810 na rota de estudos!")