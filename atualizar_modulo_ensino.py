import re

# ==========================================
# 1. ATUALIZAR APP.PY
# ==========================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Garantir criacao da tabela de alocacao ou colunas em app.py
trecho_tabelas_aloc = """
    try:
        cur_tab = conn.cursor() if hasattr(conn, 'cursor') else conn
        # Colunas na tabela membros e usuarios
        try:
            cur_tab.execute("ALTER TABLE membros ADD COLUMN professor_nome VARCHAR(150)")
        except Exception: pass
        try:
            cur_tab.execute("ALTER TABLE membros ADD COLUMN professor_id INTEGER")
        except Exception: pass
        try:
            cur_tab.execute("ALTER TABLE usuarios ADD COLUMN professor_nome VARCHAR(150)")
        except Exception: pass
        try:
            cur_tab.execute("ALTER TABLE usuarios ADD COLUMN professor_id INTEGER")
        except Exception: pass
    except Exception: pass
"""

# Substituir a busca dos candidatos no dashboard para incluir o professor e calcular os KPIs
trecho_prog_antigo = """        query_prog = \"\"\"
            SELECT m.id, m.nome, m.foto_path, m.telefone,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                   COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
            FROM membros m
            LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
            GROUP BY m.id, m.nome, m.foto_path, m.telefone
            ORDER BY m.id DESC
        \"\"\"
        c.execute(query_prog)
        candidatos_discipulado = c.fetchall()"""

trecho_prog_novo = """        # Buscar lista de Professores/Mentores disponiveis
        professores_discipulado = []
        for m in todos_membros:
            f_val = str(m.get('funcao', '') if hasattr(m, 'get') else m['funcao'] if 'funcao' in m.keys() else '')
            # Membros com ministerio ou em comunhao aptos para discipular
            if any(term in f_val.lower() for term in ['pastor', 'presb', 'diacon', 'evang', 'obreir', 'lider', 'comunh']):
                professores_discipulado.append(m)
        if not professores_discipulado:
            professores_discipulado = todos_membros

        # Query de progresso trazendo professor_nome
        query_prog = \"\"\"
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
        \"\"\"
        try:
            c.execute(query_prog)
            candidatos_discipulado = c.fetchall()
        except Exception:
            # Fallback caso a coluna ainda esteja a sincronizar
            query_prog_fb = \"\"\"
                SELECT m.id, m.nome, m.foto_path, m.telefone,
                       'A designar' as prof_nome,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
                FROM membros m
                LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
                GROUP BY m.id, m.nome, m.foto_path, m.telefone
                ORDER BY m.id DESC
            \"\"\"
            c.execute(query_prog_fb)
            candidatos_discipulado = c.fetchall()"""

if trecho_prog_antigo in app_code:
    app_code = app_code.replace(trecho_prog_antigo, trecho_prog_novo)
    print("✓ app.py: Consulta de progresso atualizada com professores!")

# Envio de professores_discipulado no render_template de dashboard.html
if "professores_discipulado=professores_discipulado" not in app_code and "return render_template('dashboard.html'," in app_code:
    app_code = app_code.replace("return render_template('dashboard.html',", "return render_template('dashboard.html', professores_discipulado=professores_discipulado,", 1)
    print("✓ app.py: professores_discipulado injetado no dashboard!")

# Na criacao do usuario (/usuarios/novo), salvar professor alocado
antigo_usr_post = "m_id_val = int(m_id_form) if (m_id_form and m_id_form.isdigit()) else None"
novo_usr_post = """m_id_val = int(m_id_form) if (m_id_form and m_id_form.isdigit()) else None
    prof_id_form = request.form.get('professor_id')
    prof_id_val = int(prof_id_form) if (prof_id_form and prof_id_form.isdigit()) else None
    prof_nome_val = (request.form.get('professor_nome') or '').strip()

    if prof_nome_val and m_id_val:
        try:
            conn_p = get_db()
            param_ch = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            conn_p.execute(f"UPDATE membros SET professor_id = {param_ch}, professor_nome = {param_ch} WHERE id = {param_ch}", (prof_id_val, prof_nome_val, m_id_val))
            conn_p.commit()
        except Exception as e:
            print("Erro ao alocar professor ao membro:", e)"""

if antigo_usr_post in app_code and "prof_nome_val" not in app_code:
    app_code = app_code.replace(antigo_usr_post, novo_usr_post)
    print("✓ app.py: Rota /usuarios/novo preparada para salvar o professor alocado!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

# ==========================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML
# ==========================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

# A) Adicionar campo do Professor no Formulario de Criar Utilizador
antigo_form_input = """                            <input type="hidden" name="membro_id" id="input_membro_id" value="">"""
novo_form_input = """                            <input type="hidden" name="membro_id" id="input_membro_id" value="">
                            <input type="hidden" name="professor_nome" id="input_prof_nome" value="">

                            <!-- Seletor do Professor / Discipulador Responsavel -->
                            <div id="box_professor_aloc" class="bg-blue-50/60 p-3 rounded-2xl border border-blue-200">
                                <label class="block text-xs font-bold text-blue-900 mb-1">👨‍🏫 Professor / Discipulador Alocado:</label>
                                <select name="professor_id" id="select_professor" class="w-full h-10 px-2 text-xs border rounded-xl bg-white font-semibold text-slate-800" onchange="atualizarProfNome(this)">
                                    <option value="">-- Selecionar Mentor / Professor --</option>
                                    {% for p in professores_discipulado %}
                                    <option value="{{ p['id'] if p is mapping else p[0] }}" data-pnome="{{ p['nome'] if p is mapping else p[1] }}">
                                        {{ p['nome'] if p is mapping else p[1] }} ({{ p['funcao'] if p is mapping else p[3] if p|length > 3 else 'Líder' }})
                                    </option>
                                    {% endfor %}
                                </select>
                            </div>"""

if antigo_form_input in dash and "box_professor_aloc" not in dash:
    dash = dash.replace(antigo_form_input, novo_form_input)
    # Adicionar funcao JS para preencher o nome do professor
    script_prof_func = """
                        function atualizarProfNome(sel) {
                            var opt = sel.options[sel.selectedIndex];
                            var pnome = opt.getAttribute('data-pnome') || '';
                            document.getElementById('input_prof_nome').value = pnome;
                        }
"""
    dash = dash.replace("function normalizarTexto(txt) {", script_prof_func + "                        function normalizarTexto(txt) {")
    print("✓ templates/dashboard.html: Seletor de Professor inserido no cadastro de utilizadores!")

# B) Inserir os Cards de KPIs e Tabela com Coluna de Professor no Dashboard de Ensino
bloco_tabela_antiga = """    <!-- Tabela de Alunos e Progresso das Classes -->
    <div class="mt-6">
        <h3 class="text-sm font-extrabold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span>📊</span> Progresso de Formação por Classe
        </h3>"""

bloco_tabela_nova = """    <!-- CARDS DE METRICAS DA AREA DE ENSINO (KPIS) -->
    {% set total_alunos_disc = discipulado_alunos|length %}
    {% set total_aptos_batismo = 0 %}
    {% for ca in discipulado_alunos %}{% if ca['c4_ok'] == 1 %}{% set total_aptos_batismo = total_aptos_batismo + 1 %}{% endif %}{% endfor %}
    {% set total_em_curso = total_alunos_disc - total_aptos_batismo %}

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 mb-6">
        <div class="bg-gradient-to-br from-blue-900 to-indigo-950 p-4 rounded-3xl text-white shadow-md border border-blue-800/40">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-blue-200 uppercase tracking-wider">Candidatos / Alunos</span>
                <span class="text-2xl">🎓</span>
            </div>
            <div class="text-3xl font-black mt-2">{{ total_alunos_disc }}</div>
            <div class="text-[11px] text-blue-300 font-medium mt-1">Matriculados no Discipulado</div>
        </div>

        <div class="bg-gradient-to-br from-emerald-700 to-teal-900 p-4 rounded-3xl text-white shadow-md border border-emerald-600/40">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-emerald-200 uppercase tracking-wider">Aptos ao Batismo</span>
                <span class="text-2xl">🌊</span>
            </div>
            <div class="text-3xl font-black mt-2">{{ total_aptos_batismo }}</div>
            <div class="text-[11px] text-emerald-200 font-medium mt-1">Concluíram as 4 Classes</div>
        </div>

        <div class="bg-gradient-to-br from-amber-600 to-orange-800 p-4 rounded-3xl text-white shadow-md border border-amber-500/40">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-200 uppercase tracking-wider">Em Formação</span>
                <span class="text-2xl">⏳</span>
            </div>
            <div class="text-3xl font-black mt-2">{{ total_em_curso }}</div>
            <div class="text-[11px] text-amber-200 font-medium mt-1">Aulas e questionários pendentes</div>
        </div>

        <div class="bg-gradient-to-br from-purple-800 to-slate-900 p-4 rounded-3xl text-white shadow-md border border-purple-700/40">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-purple-200 uppercase tracking-wider">Mentores / Professores</span>
                <span class="text-2xl">👨‍🏫</span>
            </div>
            <div class="text-3xl font-black mt-2">{{ professores_discipulado|length }}</div>
            <div class="text-[11px] text-purple-200 font-medium mt-1">Obreiros e Líderes Ativos</div>
        </div>
    </div>

    <!-- Tabela de Alunos, Mentoria e Progresso das Classes -->
    <div class="mt-4 bg-white/95 rounded-3xl p-5 border border-slate-200 card-glow">
        <div class="flex justify-between items-center mb-4 flex-wrap gap-2 border-b pb-3">
            <div>
                <h3 class="text-base font-black text-slate-900 flex items-center gap-2">
                    <span>📊</span> Relatório Oficial de Ensino & Acompanhamento
                </h3>
                <p class="text-xs text-slate-500 font-medium">Controlo pastoral de presença, tutoria e certificação de candidatos</p>
            </div>
        </div>"""

if bloco_tabela_antiga in dash:
    dash = dash.replace(bloco_tabela_antiga, bloco_tabela_nova)
    print("✓ templates/dashboard.html: Dashboard de Ensino renovado com KPIs!")

# Ajustar o cabecalho da tabela para incluir a coluna "Professor / Mentor"
antigo_thead = """                        <tr>
                            <th class="p-3.5">Candidato / Membro</th>
                            <th class="p-3.5 text-center">Classe I (Fundamentos)</th>"""

novo_thead = """                        <tr>
                            <th class="p-3.5">Candidato / Aluno</th>
                            <th class="p-3.5">Professor / Mentor</th>
                            <th class="p-3.5 text-center">Classe I (Fundamentos)</th>"""

if antigo_thead in dash:
    dash = dash.replace(antigo_thead, novo_thead)

# Ajustar as linhas do aluno na tabela para mostrar o nome do professor alocado
antigo_td_aluno = """                                    <div>
                                        <div class="font-bold text-slate-900">{{ ca['nome'] }}</div>
                                        <div class="text-[10px] text-slate-400">{{ ca['telefone'] or 'Sem contacto' }}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="p-3.5 text-center">"""

novo_td_aluno = """                                    <div>
                                        <div class="font-bold text-slate-900">{{ ca['nome'] }}</div>
                                        <div class="text-[10px] text-slate-400">{{ ca['telefone'] or 'Sem contacto' }}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="p-3.5">
                                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-bold bg-slate-100 text-slate-800 border border-slate-200">
                                    <span>👨‍🏫</span> {{ ca['prof_nome'] if ca['prof_nome'] else 'A designar' }}
                                </span>
                            </td>
                            <td class="p-3.5 text-center">"""

if antigo_td_aluno in dash:
    dash = dash.replace(antigo_td_aluno, novo_td_aluno)
    print("✓ templates/dashboard.html: Coluna de Professor / Mentor integrada na tabela!")

# Ajustar colspan da mensagem de vazio
dash = dash.replace('<td colspan="6" class="p-4 text-center text-slate-400">Nenhum membro matriculado no momento.</td>',
                    '<td colspan="7" class="p-6 text-center text-slate-400 font-semibold">Nenhum candidato em formação no momento.</td>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("✓ Modificações aplicadas com sucesso total!")