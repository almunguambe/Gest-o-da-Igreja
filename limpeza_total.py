import os
import re

print("Iniciando a limpeza e correcao do sistema...")

# 1. ATUALIZAR PYTHON (APP.PY) - Substituir a rota para ser 100% segura
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
        nome_actividade = fd.get('nome_actividade', fd.get('actividade', 'Atividade não especificada'))
        data_prevista = fd.get('data_prevista', fd.get('data', ''))
        frequencia = fd.get('frequencia', '')
        responsavel = fd.get('responsavel_directo', fd.get('responsavel', ''))
        contacto = fd.get('contacto', fd.get('telefone', ''))
        
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
        try:
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception as e:
            print("Erro BD:", e)
        return redirect('/secretaria/planificacao/nova')

    planos = []
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
        cols = [desc[0] for desc in cur.description]
        planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception:
        pass

    ficheiro_exato = 'nova_planificacao.html'
    pasta_tpl = 'templates'
    if os.path.exists(pasta_tpl):
        for r, d, files in os.walk(pasta_tpl):
            for file in files:
                if file.endswith('.html'):
                    caminho = os.path.join(r, file)
                    with open(caminho, 'r', encoding='utf-8') as f_html:
                        if 'Gravar Planificação' in f_html.read():
                            ficheiro_exato = os.path.relpath(caminho, pasta_tpl).replace(os.sep, '/')
                            break

    return render_template(ficheiro_exato, planificacoes=planos)
"""

padrao_rota = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\nif __name__ ==)"
if re.search(padrao_rota, code, re.DOTALL):
    code = re.sub(padrao_rota, nova_rota.strip() + "\n\n", code, flags=re.DOTALL)
else:
    code = code.replace("if __name__ ==", nova_rota.strip() + "\n\nif __name__ ==")
    
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("✓ Rota de Planificacao reconstruida!")

# 2. LIMPAR O HTML DAS AULAS E DA PLANIFICAÇÃO
pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                original = conteudo
                
                # Remover Certificado das Lições
                if 'Sair da Sala' in conteudo and 'Lição' in conteudo:
                    conteudo = re.sub(r'<a[^>]*>.*?Certificado.*?</a>', '', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'<button[^>]*>.*?Certificado.*?</button>', '', conteudo, flags=re.IGNORECASE)
                
                # Limpar e corrigir Planificação
                if 'Gravar Planificação' in conteudo or 'A gravar' in conteudo:
                    conteudo = re.sub(r'<!-- SUPER MOTOR DE GRAVACAO -->.*?</script>', '', conteudo, flags=re.IGNORECASE | re.DOTALL)
                    conteudo = re.sub(r'<button[^>]*>A gravar\.\.\. Aguarde!</button>', '<button type="submit" class="btn btn-primary" style="width: 100%; padding: 12px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">Gravar Planificação</button>', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'<form[^>]*>', '<form action="/secretaria/planificacao/nova" method="POST">', conteudo, flags=re.IGNORECASE)
                    
                    conteudo = re.sub(r'placeholder=["\'](Ex: Seminário.*?)["\']', r'name="nome_actividade" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'placeholder=["\'](Odete.*?)["\']', r'name="responsavel_directo" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'placeholder=["\'](825.*?)["\']', r'name="contacto" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'type=["\']date["\']', r'type="date" name="data_prevista"', conteudo, flags=re.IGNORECASE)
                    
                    for _ in range(3):
                        conteudo = conteudo.replace('name="nome_actividade" name="nome_actividade"', 'name="nome_actividade"')
                        conteudo = conteudo.replace('name="data_prevista" name="data_prevista"', 'name="data_prevista"')

                if original != conteudo:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Ficheiro limpo e corrigido: {file}")

print("✓ Processo finalizado!")