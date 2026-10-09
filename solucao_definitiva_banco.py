import os
import shutil
import ast
import re

print("=" * 65)
print("A REPARAR O MOTOR DA PLANIFICAÇÃO E A TRANSAÇÃO DO BANCO...")
print("=" * 65)

# 1. BACKUP
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
    print("✓ Backup criado: app.py.bak")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 2. ROTA TOTALMENTE BLINDADA E COM DIAGNÓSTICO ATIVO
nova_rota = '''
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    tipo_conn = str(type(conn)).lower()
    is_pg = ('psycopg' in tipo_conn) or hasattr(conn, 'cursor_factory') or ('postgres' in tipo_conn)

    # Limpeza de qualquer transacção pendente no PostgreSQL
    if hasattr(conn, 'rollback'):
        try: conn.rollback()
        except: pass

    # Criação garantida da tabela
    try:
        if is_pg:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id SERIAL PRIMARY KEY,
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
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e_tab:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        print("[AVISO CRIACAO TABELA]:", e_tab)

    # 1. PROCESSAR O FORMULÁRIO (POST)
    if request.method == 'POST':
        fd = request.form
        departamento = (fd.get('departamento') or 'Geral').strip()
        tipo_evento = (fd.get('tipo_evento') or fd.get('tipo') or 'Geral').strip()
        nome_actividade = (fd.get('nome_actividade') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data_prevista = (fd.get('data_prevista') or fd.get('data') or '').strip()
        frequencia = (fd.get('frequencia') or 'Pontual / Única').strip()
        responsavel = (fd.get('responsavel_directo') or fd.get('responsavel') or '').strip()
        contacto = (fd.get('contacto') or fd.get('telefone') or '').strip()

        data_final = data_prevista if data_prevista else '---'

        marcador = "%s" if is_pg else "?"
        sql = f"""INSERT INTO planificacoes 
                 (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')"""
        
        try:
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_final, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'): conn.commit()
            return redirect('/secretaria/planificacao/nova')
        except Exception as e_post:
            if hasattr(conn, 'rollback'):
                try: conn.rollback()
                except: pass
            # SE HOUVER ERRO NO BANCO, EXIBE NA TELA
            return f"""
            <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 50px auto; padding: 25px; background: #fff1f2; border: 2px solid #e11d48; border-radius: 12px;">
                <h2 style="color: #e11d48; margin-top: 0;">⚠️ O Supabase Rejeitou a Gravação</h2>
                <p style="color: #334155;">Mensagem retornada pela Base de Dados:</p>
                <pre style="background: white; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px; color: #991b1b; white-space: pre-wrap;">{str(e_post)}</pre>
                <div style="margin-top: 20px;">
                    <a href="/secretaria/planificacao/nova" style="display: inline-block; padding: 10px 20px; background: #3730a3; color: white; border-radius: 6px; text-decoration: none; font-weight: bold;">
                        ← Voltar e Tentar Novamente
                    </a>
                </div>
            </div>
            """, 500

    # 2. LEITURA DOS DADOS (GET)
    planos = []
    try:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur.execute("SELECT id, departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status FROM planificacoes ORDER BY id DESC")
        registos = cur.fetchall()
        if cur.description:
            colunas = [d[0] for d in cur.description]
            for reg in registos:
                if isinstance(reg, dict):
                    planos.append(reg)
                elif hasattr(reg, 'keys'):
                    planos.append(dict(reg))
                else:
                    planos.append(dict(zip(colunas, reg)))
    except Exception as e_get:
        print("[ERRO LEITURA PLANOS]:", e_get)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    tpl_nome = 'nova_planificacao.html'
    for t in ['nova_planificacao.html', 'planificacao_nova.html', 'secretaria_planos.html']:
        if os.path.exists(os.path.join('templates', t)):
            tpl_nome = t
            break

    return render_template(tpl_nome, planificacoes=planos, planos=planos)
'''

# 3. SUBSTITUIÇÃO CIRÚRGICA DA ROTA NO APP.PY
linhas = code.splitlines(keepends=True)
novas_linhas = []
ignorar = False
substituiu = False

for l in linhas:
    if "@app.route('/secretaria/planificacao/nova'" in l:
        ignorar = True
        novas_linhas.append(nova_rota.strip() + "\n\n")
        substituiu = True
        continue
    if ignorar:
        if (l.startswith("@app.") or l.startswith("def ") or l.startswith("# MOTOR")) and "planificacao_nova" not in l:
            ignorar = False
            novas_linhas.append(l)
        continue
    novas_linhas.append(l)

if not substituiu:
    novas_linhas.append("\n\n" + nova_rota.strip() + "\n")

code_final = "".join(novas_linhas)

# 4. VALIDAÇÃO DE SINTAXE COM AST
try:
    ast.parse(code_final)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_final)
    print("✓ Backend app.py atualizado e 100% validado pelo compilador Python!")
except SyntaxError as e:
    print(f"❌ Erro de compilação: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

print("=" * 65)
print("✓ TUDO CONCLUÍDO COM SUCESSO!")
print("=" * 65)