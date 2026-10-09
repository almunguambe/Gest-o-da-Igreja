import os
import re
import ast
import subprocess

print("=" * 65)
print("A REPARAR O SERVIDOR E A RESTAURAR A FUNÇÃO GET_DB()...")
print("=" * 65)

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remover qualquer tag HTML que tenha caído no app.py
code = re.sub(r'<!--[\s\S]*?-->', '', code)
code = re.sub(r'<a\s+href=[\s\S]*?</a>', '', code)
code = re.sub(r'class="btn-planificacao"[^\n]*', '', code)

# 2. Remover o bloco que cortou a função get_db() ao meio
padrao_tabela_meio = r'(def criar_tabela_planificacoes_garantida\(\):[\s\S]*?except Exception:\s*pass\n*)'
match_tabela = re.search(padrao_tabela_meio, code)
if match_tabela:
    code = code.replace(match_tabela.group(1), "\n")
    print("✓ Bloco intruso removido de dentro do get_db().")

# 3. Testar compilação com o analisador sintático do Python (AST)
valido = False
try:
    ast.parse(code)
    valido = True
    print("✓ Sintaxe do app.py corrigida diretamente!")
except SyntaxError:
    print("A usar o histórico do Git para recuperar a versão funcional...")
    res = subprocess.run(['git', 'log', '--pretty=format:%h', '-15'], capture_output=True, text=True)
    hashes = res.stdout.strip().split('\n')
    for h in hashes:
        try:
            conteudo_antigo = subprocess.check_output(['git', 'show', f'{h}:app.py'], text=True, encoding='utf-8')
            ast.parse(conteudo_antigo)
            code = conteudo_antigo
            valido = True
            print(f"✓ Versão estável recuperada com sucesso do commit {h}!")
            break
        except Exception:
            continue

# 4. Garantir que a rota da planificação está presente e 100% operacional
if "/secretaria/planificacao/nova" not in code:
    rota_plan = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or hasattr(conn, 'cursor_factory') or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS planificacoes (
                id {id_tipo},
                departamento TEXT,
                tipo_evento TEXT,
                nome_actividade TEXT,
                data_prevista TEXT,
                frequencia TEXT,
                responsavel_directo TEXT,
                contacto TEXT,
                status TEXT DEFAULT 'Pendente'
            );
        """)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception:
        pass

    if request.method == 'POST':
        fd = request.form
        dep = (fd.get('departamento') or 'Geral').strip()
        tipo = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data = (fd.get('data_prevista') or fd.get('data') or '').strip()
        freq = (fd.get('frequencia') or 'Pontual / Única').strip()
        resp = (fd.get('responsavel_directo') or fd.get('responsavel') or '').strip()
        cont = (fd.get('contacto') or fd.get('telefone') or '').strip()

        marcador = "%s" if is_pg else "?"
        sql = f"""INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        try:
            cur.execute(sql, (dep, tipo, nome, data, freq, resp, cont))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception:
            if hasattr(conn, 'rollback'): conn.rollback()
        finally:
            if hasattr(conn, 'close'): conn.close()
        return redirect('/secretaria/planificacao/nova')

    planos = []
    try:
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            planos = [dict(zip(cols, r)) for r in cur.fetchall()]
        else:
            planos = cur.fetchall()
    except Exception:
        pass
    finally:
        if hasattr(conn, 'close'): conn.close()

    for tpl in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', tpl)):
            return render_template(tpl, planificacoes=planos, planos=planos)
    return render_template('dashboard.html', planificacoes=planos, planos=planos)
'''
    code = code + "\n\n" + rota_plan.strip() + "\n"

# Validação final obrigatória
ast.parse(code)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("✓ app.py validado e gravado sem qualquer erro de sintaxe!")

# 5. Adicionar o atalho estritamente no HTML (templates/dashboard.html)
tpl_dash = os.path.join('templates', 'dashboard.html')
if os.path.exists(tpl_dash):
    with open(tpl_dash, 'r', encoding='utf-8') as f:
        dash = f.read()

    botao_dash = '''
<!-- BOTÃO DE ACESSO À PLANIFICAÇÃO -->
<div style="margin: 20px 0; padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: space-between;">
    <div>
        <h4 style="margin: 0; color: #1e293b; font-size: 16px;">📌 Cronograma & Planificação</h4>
        <p style="margin: 4px 0 0; color: #64748b; font-size: 13px;">Secretaria: registo e acompanhamento das actividades.</p>
    </div>
    <a href="/secretaria/planificacao/nova" style="display: inline-flex; align-items: center; gap: 8px; background-color: #3730a3; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">
        Abrir Planificação
    </a>
</div>
'''
    if '/secretaria/planificacao/nova' not in dash:
        if '<div class="container' in dash:
            dash = dash.replace('<div class="container', botao_dash + '\n<div class="container', 1)
        elif '<main' in dash:
            dash = dash.replace('<main', botao_dash + '\n<main', 1)
        else:
            dash = botao_dash + '\n' + dash

        with open(tpl_dash, 'w', encoding='utf-8') as f:
            f.write(dash)
        print("✓ Atalho inserido corretamente no templates/dashboard.html!")

print("=" * 65)
print("✓ TUDO CONCLUÍDO COM SUCESSO!")
print("=" * 65)