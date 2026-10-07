import os
import re

# 1. ATUALIZAR O APP.PY PARA GRAVAR NA BASE DE DADOS
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

alvo = "# Aqui ficará o código de gravação do plano futuramente"
logica_db = """
        conn = get_db()
        # Captura os dados vindos do HTML
        departamento = request.form.get('departamento', '')
        tipo_evento = request.form.get('tipo_evento', '')
        nome_actividade = request.form.get('nome_actividade', '')
        data_prevista = request.form.get('data_prevista', '')
        frequencia = request.form.get('frequencia', '')
        responsavel = request.form.get('responsavel_directo', '')
        contacto = request.form.get('contacto', '')
        
        # Envia para o Supabase
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')'''
        try:
            conn.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
        except Exception as e:
            print("Erro ao gravar planificacao:", e)
"""

if alvo in code:
    code = code.replace(alvo, logica_db.strip())
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Lógica de gravação ativada no app.py")

# 2. DESTRAVAR O FORMULÁRIO HTML
pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                original = conteudo
                
                if 'Gravar Planificação' in conteudo:
                    # Forçar o form a ser POST e enviar dados
                    if '<form' in conteudo and 'method=' not in conteudo.lower():
                        conteudo = conteudo.replace('<form', '<form method="POST"')
                    # Tirar atributos required silenciosos que bloqueiam o botão
                    conteudo = re.sub(r'\brequired(="[^"]*")?', '', conteudo, flags=re.IGNORECASE)
                    # Garantir que o botão sabe que tem de submeter (type="submit")
                    if 'type="submit"' not in conteudo:
                        conteudo = re.sub(r'<button([^>]*)>\s*Gravar Planificação', r'<button type="submit"\1>Gravar Planificação', conteudo, flags=re.IGNORECASE)

                if conteudo != original:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Botão e Formulário destravados no ficheiro: {file}")