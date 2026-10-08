import os
import re

print("A iniciar a cura segura e definitiva do sistema...")

# 1. LIMPAR O GATILHO QUE CONGELA O BOTÃO
pasta = 'templates'
if os.path.exists(pasta):
    for r, d, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(r, file)
                with open(path, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                original = html
                
                # Apaga os scripts invisíveis que bloqueiam o ecrã
                html = re.sub(r'<!-- GATILHO INFALÍVEL -->.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
                html = re.sub(r'<!-- TECNOLOGIA AJAX.*?-->.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
                html = re.sub(r'<!-- SUPER MOTOR.*?-->.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
                html = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded".*?Destruir botao.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
                
                if original != html:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"✓ Botão descongelado no ficheiro: {file}")

# 2. COLOCAR A GRAVAÇÃO BLINDADA NO APP.PY
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

padrao = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\n# MOTOR|\nif __name__|\Z)"

rota_segura = """@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import render_template, request, redirect
    import os
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    except Exception as e:
        return f"<h1 style='color:red;'>Erro ao ligar: {e}</h1>"

    if request.method == 'POST':
        fd = request.form
        departamento = fd.get('departamento', 'Não definido')
        tipo_evento = fd.get('tipo_evento', fd.get('tipo', 'Não definido'))
        nome_actividade = fd.get('nome_actividade', fd.get('actividade', 'Não definido'))
        data_prevista = fd.get('data_prevista', '')
        frequencia = fd.get('frequencia', 'Não definido')
        responsavel = fd.get('responsavel_directo', fd.get('responsavel', 'Não definido'))
        contacto = fd.get('contacto', fd.get('telefone', 'Não definido'))
        
        # Proteção do PostgreSQL contra datas vazias (Evita falhas em silêncio)
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
            sql_final = sql if is_pg else sql.replace('%s', '?')
            cur.execute(sql_final, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
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

if re.search(padrao, code, flags=re.DOTALL):
    code = re.sub(padrao, rota_segura, code, flags=re.DOTALL)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Motor app.py protegido e curado!")
else:
    print("Aviso: Rota não encontrada no app.py.")

print("✓ TUDO PRONTO! Pode enviar para a nuvem.")