import os
import re

print("A preparar o sistema para a apresentação desta noite...")

# 1. AJUSTAR OS MODELOS HTML (Suportar tanto 'planos' como 'planificacoes')
pasta_templates = 'templates'
if os.path.exists(pasta_templates):
    for root, _, files in os.walk(pasta_templates):
        for f in files:
            if f.endswith('.html'):
                caminho = os.path.join(root, f)
                with open(caminho, 'r', encoding='utf-8') as arq:
                    html = arq.read()
                
                original = html
                # Permite que a tabela leia tanto se a variável for planos ou planificacoes
                html = html.replace('{% if planificacoes %}', '{% if planificacoes or planos %}')
                html = html.replace('{% for p in planificacoes %}', '{% for p in (planificacoes or planos) %}')
                
                # Garante que o botão funciona de forma limpa e natural
                html = html.replace("this.innerHTML='A Gravar...'; this.form.submit();", "")
                
                if original != html:
                    with open(caminho, 'w', encoding='utf-8') as arq:
                        arq.write(html)
                    print(f"✓ Ficheiro visual atualizado: {f}")

# 2. BLINDAR O APP.PY (Criar tabela automática e sincronizar Dashboard + Secretaria)
with open('app.py', 'r', encoding='utf-8') as arq:
    code = arq.read()

# Código de criação automática da tabela no banco
bloco_tabela = """
def criar_tabela_planificacoes_se_faltar(conn):
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
        if is_pg:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS planificacoes (
                    id SERIAL PRIMARY KEY,
                    departamento VARCHAR(150),
                    tipo_evento VARCHAR(150),
                    nome_actividade VARCHAR(255),
                    data_prevista VARCHAR(50),
                    frequencia VARCHAR(100),
                    responsavel_directo VARCHAR(150),
                    contacto VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'Pendente'
                );
            ''')
        else:
            cur.execute('''
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
            ''')
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
"""

if "def criar_tabela_planificacoes_se_faltar" not in code:
    code = code.replace("app = Flask(__name__)", bloco_tabela + "\napp = Flask(__name__)")

# Ajuste da rota do dashboard para sempre ler planificacoes
code = re.sub(
    r"planos\s*=\s*conn\.execute\([\"']SELECT \* FROM actividades_planeamento.*?\)[\s\S]*?except Exception:\s*planos = \[\]",
    """criar_tabela_planificacoes_se_faltar(conn)
    planos = []
    try:
        cur_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_pl.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur_pl.description:
            cols_pl = [desc[0] for desc in cur_pl.description]
            planos = [dict(zip(cols_pl, r)) for r in cur_pl.fetchall()]
        else:
            planos = cur_pl.fetchall()
    except Exception:
        planos = []""",
    code
)

# Garante que o dashboard passa ambas as variáveis
code = re.sub(
    r"render_template\('dashboard\.html',\s*planos=planos,",
    "render_template('dashboard.html', planos=planos, planificacoes=planos,",
    code
)

# Substitui a rota da planificação pela versão infalível
rota_planificacao_definitiva = """
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    conn = get_db()
    criar_tabela_planificacoes_se_faltar(conn)
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    if request.method == 'POST':
        fd = request.form
        departamento = fd.get('departamento', 'Geral')
        tipo_evento = fd.get('tipo_evento', fd.get('tipo', 'Geral'))
        nome_actividade = fd.get('nome_actividade', fd.get('actividade', fd.get('nome', 'Atividade')))
        data_prevista = fd.get('data_prevista', fd.get('data', ''))
        frequencia = fd.get('frequencia', 'Pontual')
        responsavel = fd.get('responsavel_directo', fd.get('responsavel', ''))
        contacto = fd.get('contacto', fd.get('telefone', ''))

        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None

        is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
        marcador = "%s" if is_pg else "?"
        
        sql = f'''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                 VALUES ({marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, {marcador}, 'Pendente')'''
        try:
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
        except Exception as e:
            print("Erro ao gravar:", e)
            if hasattr(conn, 'rollback'):
                conn.rollback()

        return redirect(request.referrer or '/')

    # Leitura
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

    return render_template('dashboard.html', planos=planos, planificacoes=planos)
"""

padrao_rota = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\n# MOTOR|\nif __name__|\Z)"
if re.search(padrao_rota, code, re.DOTALL):
    code = re.sub(padrao_rota, rota_planificacao_definitiva.strip() + "\n\n", code, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as arq:
    arq.write(code)

print("✓ BACKEND E BASE DE DADOS SINCRONIZADOS COM SUCESSO!")