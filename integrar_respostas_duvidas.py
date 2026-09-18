import os

with open("app.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Atualizar a rota /dashboard para carregar a lista de duvidas para o Pastor
antiga_linha_dashboard = "lista_avaliacoes = conn.execute(\"SELECT * FROM avaliacoes_estudantes ORDER BY id DESC\").fetchall()"
nova_linha_dashboard = """lista_avaliacoes = conn.execute("SELECT * FROM avaliacoes_estudantes ORDER BY id DESC").fetchall()
    todas_duvidas = conn.execute("SELECT * FROM duvidas_estudantes ORDER BY id DESC").fetchall()"""

if antiga_linha_dashboard in codigo and "todas_duvidas" not in codigo:
    codigo = codigo.replace(antiga_linha_dashboard, nova_linha_dashboard)
    codigo = codigo.replace("lista_avaliacoes=lista_avaliacoes,", "lista_avaliacoes=lista_avaliacoes,\n                           todas_duvidas=todas_duvidas,")

# 2. Atualizar a rota /estudos para carregar as duvidas do próprio aluno logado
antiga_rota_estudos = """@app.route('/estudos')
def portal_estudos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    resultado_teste = session.pop('resultado_teste', None)
    tel_admin = "258866677810"
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_admin)"""

nova_rota_estudos = """@app.route('/estudos')
def portal_estudos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    resultado_teste = session.pop('resultado_teste', None)
    usuario = session.get('usuario')
    
    conn = get_db()
    param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    minhas_duvidas = conn.execute(f"SELECT * FROM duvidas_estudantes WHERE usuario = {param_char} ORDER BY id DESC", (usuario,)).fetchall()
    conn.close()

    tel_admin = "258866677810"
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_admin, minhas_duvidas=minhas_duvidas)"""

if antiga_rota_estudos in codigo:
    codigo = codigo.replace(antiga_rota_estudos, nova_rota_estudos)
else:
    # Caso tenha ligeira variação no retorno da rota
    codigo = codigo.replace(
        "return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_admin)",
        """conn = get_db()
    param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    minhas_duvidas = conn.execute(f"SELECT * FROM duvidas_estudantes WHERE usuario = {param_char} ORDER BY id DESC", (session.get('usuario'),)).fetchall()
    conn.close()
    return render_template('estudos.html', resultado_teste=resultado_teste, tel_pastor=tel_admin, minhas_duvidas=minhas_duvidas)"""
    )

# 3. Rota para o Pastor responder a dúvida do aluno
rota_responder_pastor = """
@app.route('/estudos/duvidas/responder/<int:id>', methods=['POST'])
def responder_duvida_pastor(id):
    if not (is_admin() or can_cadastro()):
        return redirect(url_for('dashboard'))
    
    resposta = request.form.get('resposta', '').strip()
    if resposta:
        conn = get_db()
        param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
        conn.execute(f"UPDATE duvidas_estudantes SET resposta = {param_char} WHERE id = {param_char}", (resposta, id))
        conn.commit()
        conn.close()
        session['sucesso_cadastro'] = "Resposta pastoral enviada com sucesso para a sala de aula do aluno!"
    
    return redirect(url_for('dashboard'))
"""

if "/estudos/duvidas/responder" not in codigo:
    codigo = codigo.replace("if __name__ == '__main__':", rota_responder_pastor + "\nif __name__ == '__main__':")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✓ app.py atualizado com sistema bidirecional de perguntas e respostas!")