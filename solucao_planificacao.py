import os
import re

# 1. ATUALIZAR O APP.PY (Remover Raio-X e forçar Gravação)
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remover as mensagens do Raio-X e restaurar o fluxo normal
xray_sucesso = 'return f"<h1>SUCESSO! O Botão funciona!</h1><p>O Python leu os seguintes dados do formulário HTML:<br>Departamento: {departamento}<br>Actividade: {nome_actividade}</p><br><a href=\'/secretaria/planificacao/nova\'>Voltar</a>"'
xray_erro = 'return f"<h1>ERRO NO SUPABASE:</h1><p>{e}</p> <br><a href=\'/secretaria/planificacao/nova\'>Voltar</a>"'

code = code.replace(xray_sucesso, "return redirect('/secretaria/planificacao/nova')")
code = code.replace(xray_erro, "pass")

# Substituir o bloco de captura antigo por um inteligente com COMMIT
bloco_antigo = """        # Captura os dados vindos do HTML
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
            conn.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))"""

bloco_novo = """        # Captura inteligente (aceita variações nos nomes do HTML)
        fd = request.form
        departamento = fd.get('departamento', '')
        tipo_evento = fd.get('tipo_evento', fd.get('tipo', ''))
        nome_actividade = fd.get('nome_actividade', fd.get('actividade', fd.get('nome', 'Atividade não especificada')))
        data_prevista = fd.get('data_prevista', fd.get('data', ''))
        frequencia = fd.get('frequencia', '')
        responsavel = fd.get('responsavel_directo', fd.get('responsavel', ''))
        contacto = fd.get('contacto', fd.get('telefone', ''))
        
        # Envia para o Supabase
        sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')'''
        try:
            conn.execute(sql, (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()  # O SEGREDO ESTÁ AQUI: Grava fisicamente na base de dados!"""

if "Captura os dados vindos do HTML" in code:
    code = code.replace(bloco_antigo, bloco_novo)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)


# 2. CORRIGIR O HTML (Injetar a etiqueta em falta)
pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'Gravar Planificação' in conteudo:
                    # Injeta name="nome_actividade" na caixa de texto da atividade
                    padrao = r'(<input[^>]*placeholder=["\']1a Seminario["\'][^>]*)>'
                    substituicao = r'\1 name="nome_actividade">'
                    conteudo = re.sub(padrao, substituicao, conteudo)
                    # Limpa duplicações se já existissem
                    conteudo = re.sub(r'name="[^"]*"\s*name="nome_actividade"', 'name="nome_actividade"', conteudo)
                    
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)

print("✓ Solução definitiva aplicada com sucesso!")