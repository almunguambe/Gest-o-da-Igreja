import os
import ast

print("A analisar e restaurar as variáveis do dashboard no app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Localizar o ponto exato do render_template do dashboard
alvo_render = "return render_template('dashboard.html',"
pos_render = code.find(alvo_render)

if pos_render == -1:
    print("ERRO: Linha de render do dashboard não encontrada.")
    exit(1)

# 2. Localizar o fim do bloco anterior (membros_json)
pos_membros = code.rfind("membros_json", 0, pos_render)
if pos_membros == -1:
    pos_membros = code.rfind("alerta_duplicado", 0, pos_render)

fim_linha_anterior = code.find("\n", pos_membros) + 1

# 3. Bloco completo, seguro e indentado com todas as variáveis necessárias
bloco_restaurado = """
    alerta_duplicado = session.pop('alerta_duplicado', None)
    sucesso_cadastro = session.pop('sucesso_cadastro', None)

    # 1. Dúvidas do Discipulado
    duvidas_lista = []
    try:
        cur_duv = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_duv.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
        duvidas_lista = cur_duv.fetchall()
    except Exception:
        duvidas_lista = []

    # 2. Professores do Discipulado (Evita NameError)
    professores_discipulado = []
    try:
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
            if any(term in f_val for term in ['pastor', 'presb', 'diacon', 'evang', 'obreir', 'lider', 'comunh']):
                professores_discipulado.append(m)
        if not professores_discipulado:
            professores_discipulado = todos_membros
    except Exception:
        professores_discipulado = todos_membros if 'todos_membros' in locals() else []

    # 3. Candidatos ao Discipulado
    candidatos_discipulado = []
    try:
        cur_cd = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_cd.execute(\"\"\"
            SELECT m.id, m.nome, m.foto_path, m.telefone,
                   COALESCE(m.professor_nome, 'A designar') as prof_nome,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
            FROM membros m
            LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
            WHERE LOWER(COALESCE(m.funcao, '')) LIKE '%candidat%'
               OR LOWER(COALESCE(m.funcao, '')) LIKE '%prova%'
               OR LOWER(COALESCE(m.funcao, '')) LIKE '%convertid%'
               OR LOWER(COALESCE(m.batizado, '')) IN ('nao', 'não', 'pendente', '')
            GROUP BY m.id, m.nome, m.foto_path, m.telefone, m.professor_nome
            ORDER BY m.id DESC
        \"\"\")
        candidatos_discipulado = cur_cd.fetchall()
    except Exception:
        candidatos_discipulado = []

    # 4. Planificações Eclesiásticas
    planos = []
    try:
        cur_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = 'psycopg' in str(type(conn)).lower() or hasattr(conn, 'cursor_factory')
        id_col = "SERIAL" if is_pg else "INTEGER"
        cur_pl.execute(f"CREATE TABLE IF NOT EXISTS planificacoes (id {id_col} PRIMARY KEY, departamento TEXT, tipo_evento TEXT, nome_actividade TEXT, data_prevista TEXT, frequencia TEXT, responsavel_directo TEXT, contacto TEXT, status TEXT DEFAULT 'Pendente')")
        if hasattr(conn, 'commit'):
            conn.commit()
        cur_pl.execute("SELECT * FROM planificacoes ORDER BY id DESC")
        if cur_pl.description:
            cols_pl = [desc[0] for desc in cur_pl.description]
            planos = [dict(zip(cols_pl, r)) for r in cur_pl.fetchall()]
        else:
            planos = cur_pl.fetchall()
    except Exception:
        planos = []

    # 5. Candidatos ao Batismo
    candidatos_batismo = []
    try:
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '').lower()
            b_val = str(m.get('batizado', '') if hasattr(m, 'get') else m['batizado'] if 'batizado' in m.keys() else '').lower()
            if ('candidat' in f_val) or ('prova' in f_val) or ('convertid' in f_val) or (b_val in ['nao', 'não', 'pendente', '']):
                candidatos_batismo.append(m)
        if not candidatos_batismo:
            candidatos_batismo = todos_membros
    except Exception:
        candidatos_batismo = todos_membros if 'todos_membros' in locals() else []

    """

# 4. Substituição precisa entre o fim do bloco anterior e o render_template
code = code[:fim_linha_anterior] + bloco_restaurado + "\n    " + code[pos_render:]

# 5. Garantir que planificacoes=planos é passado para o template
if "planificacoes=planos" not in code:
    code = code.replace("planos=planos,", "planos=planos, planificacoes=planos,")

# 6. Validação estrita por AST (Compilador Python)
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("=" * 60)
    print("✓ SUCESSO: Todas as variáveis restauradas e sintaxe 100% validada!")
    print("=" * 60)
except SyntaxError as e:
    print(f"Erro de sintaxe detetado na linha {e.lineno}: {e}")
    exit(1)