import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

nova_rota = """
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import render_template, request, redirect
    import os
    
    conn = get_db()
    if request.method == 'POST':
        fd = request.form
        departamento = fd.get('departamento', '')
        tipo_evento = fd.get('tipo_evento', fd.get('tipo', ''))
        nome_actividade = fd.get('nome_actividade', fd.get('actividade', fd.get('nome', 'Atividade não especificada')))
        data_prevista = fd.get('data_prevista', fd.get('data', ''))
        frequencia = fd.get('frequencia', '')
        responsavel = fd.get('responsavel_directo', fd.get('responsavel', ''))
        contacto = fd.get('contacto', fd.get('telefone', ''))
        
        # Proteção PostgreSQL: converte data vazia para None (Nulo)
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            return redirect('/secretaria/planificacao/nova')
        except Exception as e:
            return f"<h1>ERRO DO BANCO DE DADOS:</h1><p>{str(e)}</p><br><a href='/secretaria/planificacao/nova'>Voltar</a>"

    planos = []
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
        cols = [desc[0] for desc in cur.description]
        planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        pass

    ficheiro_exato = 'nova_planificacao.html'
    pasta = 'templates'
    if os.path.exists(pasta):
        for root, dirs, files in os.walk(pasta):
            for file in files:
                if file.endswith('.html'):
                    caminho = os.path.join(root, file)
                    with open(caminho, 'r', encoding='utf-8') as f_html:
                        if 'Gravar Planificação' in f_html.read():
                            ficheiro_exato = os.path.relpath(caminho, pasta).replace(os.sep, '/')
                            break

    return render_template(ficheiro_exato, planificacoes=planos)
"""

padrao_rota = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\nif __name__ ==)"

if re.search(padrao_rota, code, re.DOTALL):
    code = re.sub(padrao_rota, nova_rota.strip() + "\n\n", code, flags=re.DOTALL)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota da Planificacao reconstruida e protegida contra datas vazias!")
else:
    print("Erro: Nao encontrei a rota da planificacao no app.py.")