import os
import re

# 1. ATUALIZAR O APP.PY (Ensinar o Python a ler a tabela)
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

if "SELECT * FROM planificacoes" not in code:
    busca = """
    # Buscar os dados para a tabela lateral
    planos = []
    try:
        conn = get_db()
        if hasattr(conn, 'cursor'):
            cur = conn.cursor()
            cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        print("Erro ao buscar planos:", e)
        
    templates_possiveis = ["""
    
    # Injeta a busca na base de dados
    code = code.replace("templates_possiveis = [", busca)
    
    # Ensina a página a receber as planificações
    code = code.replace("render_template(html)", "render_template(html, planificacoes=planos)")
    code = re.sub(r"render_template\('([^']+)'\)", r"render_template('\1', planificacoes=planos)", code)
    code = code.replace(", planificacoes=planos, planificacoes=planos", ", planificacoes=planos")

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Python configurado para ler a base de dados!")

# 2. ATUALIZAR O HTML (Criar a tabela dinâmica)
html_tabela = '''
<tbody>
  {% if planificacoes %}
    {% for p in planificacoes %}
    <tr>
      <td style="padding: 12px 15px; border-bottom: 1px solid #eee;"><strong>{{ p.nome_actividade }}</strong><br><small style="color:gray;">{{ p.departamento }}</small></td>
      <td style="padding: 12px 15px; border-bottom: 1px solid #eee;">{{ p.data_prevista }}</td>
      <td style="padding: 12px 15px; border-bottom: 1px solid #eee;">{{ p.responsavel_directo }}<br><small style="color:gray;">{{ p.contacto }}</small></td>
      <td style="padding: 12px 15px; border-bottom: 1px solid #eee;"><span style="background-color: #e0e7ff; color: #3730a3; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">{{ p.status }}</span></td>
      <td style="padding: 12px 15px; border-bottom: 1px solid #eee;"><span style="color: #0d8abc; cursor: pointer; font-size:12px; font-weight:bold;">Ver</span></td>
    </tr>
    {% endfor %}
  {% else %}
    <tr><td colspan="5" style="text-align:center; padding:30px; color:gray;">Nenhuma actividade planificada ainda. Cadastre a primeira ao lado.</td></tr>
  {% endif %}
</tbody>
'''

pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Procura a tabela estática e substitui pelo motor dinâmico
                if 'Nenhuma actividade planificada ainda' in conteudo and '{% for' not in conteudo:
                    padrao_tbody = r'<tbody[^>]*>.*?Nenhuma actividade planificada ainda.*?</tbody>'
                    if re.search(padrao_tbody, conteudo, re.IGNORECASE | re.DOTALL):
                        conteudo = re.sub(padrao_tbody, html_tabela, conteudo, flags=re.IGNORECASE | re.DOTALL)
                    else:
                        padrao_tr = r'<tr[^>]*>.*?Nenhuma actividade planificada ainda.*?</tr>'
                        conteudo = re.sub(padrao_tr, html_tabela, conteudo, flags=re.IGNORECASE | re.DOTALL)
                        
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Painel lateral ativado no ficheiro HTML: {file}")

print("✓ Tudo pronto!")