import qrcode




























































































































































































































@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
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
        
        # Proteção Rigorosa PostgreSQL: Impede erro 500 quando a data está vazia
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            return redirect('/secretaria/planificacao/nova')
        except Exception as e:
            return f"<h1 style='color:red;'>O Supabase rejeitou a gravação:</h1><p>{e}</p>"

    # Puxar dados para preencher a Tabela Lateral
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