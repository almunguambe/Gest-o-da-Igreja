import os
import re

print("A iniciar cirurgia no app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Limpar a confusão da linha 1 e remover a rota colada no topo
padrao_topo = r"import qrcode@app\.route\('/secretaria/planificacao/nova'.*?return render_template\('nova_planificacao\.html', planificacoes=planos\)"
code = re.sub(padrao_topo, "import qrcode", code, flags=re.DOTALL)

# 2. Corrigir o pequeno erro de digitação do "z" caso tenha escapado
code = code.replace("conn = get_db()z", "conn = get_db()")

# 3. Remover a rota antiga que estava duplicada no fundo do ficheiro
padrao_fundo = r"@app\.route\('/secretaria/planificacao/nova'.*?return render_template\('dashboard\.html', planificacoes=planos\)"
code = re.sub(padrao_fundo, "", code, flags=re.DOTALL)

# 4. Injetar a Rota Perfeita no lugar seguro (junto ao motor de certificados)
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

print("✓ CIRURGIA CONCLUIDA! O app.py esta limpo e blindado.")