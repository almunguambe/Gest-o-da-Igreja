@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    # 1. Ligação à Base de Dados
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    except Exception as e:
        return f"<h1 style='color:red;'>Erro ao ligar à Base de Dados: {e}</h1>"

    # 2. Processo de Gravação (Quando o botão é clicado)
    if request.method == 'POST':
        departamento = request.form.get('departamento', 'Não definido')
        tipo_evento = request.form.get('tipo_evento', 'Não definido')
        nome_actividade = request.form.get('nome_actividade', 'Não definido')
        data_prevista = request.form.get('data_prevista', '')
        frequencia = request.form.get('frequencia', 'Não definido')
        responsavel = request.form.get('responsavel_directo', 'Não definido')
        contacto = request.form.get('contacto', 'Não definido')
        
        # Proteção rigorosa para o PostgreSQL: Datas vazias têm de ser tratadas como Nulas (None)
        data_bd = data_prevista if data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            
            # Força a página a recarregar limpa após o sucesso
            return redirect('/secretaria/planificacao/nova')
        
        except Exception as e:
            # Mostra o erro se o Supabase rejeitar alguma coisa
            return f"<h1 style='color:red;'>O Supabase rejeitou a gravação:</h1><p>{e}</p><a href='/secretaria/planificacao/nova'>Tentar Novamente</a>"

    # 3. Processo de Leitura (Carregar a Tabela Lateral)
    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        print("Ainda sem dados ou erro de leitura:", e)

    # Renderiza a página e envia a lista de atividades para o HTML
    return render_template('nova_planificacao.html', planificacoes=planos)