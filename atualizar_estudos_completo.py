import os

with open("app.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Adicionar tabela de duvidas dos estudantes se nao existir
bloco_tabela_duvidas = """    c.execute(f'''CREATE TABLE IF NOT EXISTS duvidas_estudantes (
        id {pk_type},
        usuario TEXT NOT NULL,
        licao TEXT NOT NULL,
        duvida TEXT NOT NULL,
        resposta TEXT,
        data_envio TEXT NOT NULL
    )''')"""

if "duvidas_estudantes" not in codigo:
    codigo = codigo.replace("c.execute(f'''CREATE TABLE IF NOT EXISTS avaliacoes_estudantes", bloco_tabela_duvidas + "\n    c.execute(f'''CREATE TABLE IF NOT EXISTS avaliacoes_estudantes")

# 2. Adicionar rota para envio de duvidas e notificacoes
rotas_duvidas = """
@app.route('/estudos/duvida', methods=['POST'])
def enviar_duvida():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session.get('usuario')
    licao = request.form.get('licao', 'Geral')
    duvida = request.form.get('duvida', '').strip()
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    if duvida:
        conn = get_db()
        param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
        conn.execute(f"INSERT INTO duvidas_estudantes (usuario, licao, duvida, data_envio) VALUES ({param_char}, {param_char}, {param_char}, {param_char})",
                     (usuario, licao, duvida, data_agora))
        conn.commit()
        conn.close()
        session['resultado_teste'] = "A sua dúvida foi enviada com sucesso à liderança pastoral!"
    
    return redirect(url_for('portal_estudos'))
"""

if "/estudos/duvida" not in codigo:
    codigo = codigo.replace("@app.route('/estudos/responder'", rotas_duvidas + "\n@app.route('/estudos/responder'")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✓ app.py atualizado com a tabela e rota de dúvidas dos alunos!")