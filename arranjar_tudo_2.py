import os
import re

print("A iniciar varredura e limpeza total do app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Destruir TODAS as versões soltas da rota planificacao_nova espalhadas pelo ficheiro
# Este padrão procura qualquer bloco que comece com @app.route('/secretaria/planificacao/nova'
# e apaga-o até à próxima rota (@app.route) ou até ao fim do ficheiro.
padrao_apagar_todas = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\Z)"
code = re.sub(padrao_apagar_todas, "", code, flags=re.DOTALL)

# 2. Garantir que o ficheiro não começa com lixo e tem os imports certos
code = code.replace("import qrcode@app.route", "import qrcode\n")
code = code.replace("import qrcode\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", "import qrcode\n")
code = code.replace("conn = get_db()z", "conn = get_db()")

# 3. Injetar a Rota Perfeita UMA ÚNICA VEZ no local seguro
rota_perfeita = """
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import render_template, request, redirect
    import os
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    except Exception as e:
        return f"<h1 style='color:red;'>Erro ao ligar à Base de Dados: {e}</h1>"

    if request.method == 'POST':
        departamento = request.form.get('departamento', 'Não definido')
        tipo_evento = request.form.get('tipo_evento', 'Não definido')
        nome_actividade = request.form.get('nome_actividade', 'Não definido')
        data_prevista = request.form.get('data_prevista', '')
        frequencia = request.form.get('frequencia', 'Não definido')
        responsavel = request.form.get('responsavel_directo', 'Não definido')
        contacto = request.form.get('contacto', 'Não definido')
        
        # Proteção Rigorosa PostgreSQL: Impede erro 500
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            return redirect('/secretaria/planificacao/nova')
        except Exception as e:
            return f"<h1 style='color:red;'>O Supabase rejeitou a gravação:</h1><p>{str(e)}</p>"

    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception:
        pass

    ficheiro_html = 'nova_planificacao.html'
    for tpl in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', tpl)):
            ficheiro_html = tpl
            break

    return render_template(ficheiro_html, planificacoes=planos)
"""

code = code.replace("# MOTOR DE EXTRAÇÃO PARA CERTIFICADOS EM PDF", rota_perfeita.strip() + "\n\n# MOTOR DE EXTRAÇÃO PARA CERTIFICADOS EM PDF")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ VARREDURA CONCLUÍDA! O app.py está livre de cópias fantasmas.")