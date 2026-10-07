import re

# 1. Atualizar templates/dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

bloco_form_antigo = """                        <form action="/usuarios/novo" method="POST" class="space-y-3">
                            <input type="text" name="usuario" required placeholder="Login *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            <input type="password" name="senha" required placeholder="Palavra-passe *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            <select name="cargo" required class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white font-bold text-blue-950">
                                <option value="Secretário">Secretário (Cadastro & Atos)</option>
                                <option value="Líder">Líder de Ministério</option>
                                <option value="Tesoureiro">Tesoureiro (Tesouraria & Dashboard)</option>
                                <option value="Estudante">Estudante (Apenas Área de Estudos)</option>
                                <option value="Pastor">Pastor (Administrador Geral)</option>
                            </select>
                            <button type="submit" class="w-full h-12 bg-emerald-700 text-white font-black text-sm rounded-2xl shadow">Criar Utilizador</button>
                        </form>"""

bloco_form_novo = """                        <form action="/usuarios/novo" method="POST" class="space-y-3">
                            <!-- Seletor de Candidatos ao Batismo -->
                            <div>
                                <label class="block text-xs font-bold text-slate-600 mb-1">Candidato ao Batismo (Aluno de Discipulado):</label>
                                <select id="select_candidato_membro" class="w-full h-11 px-2 text-sm border-2 border-indigo-200 rounded-xl bg-indigo-50/50 font-medium text-slate-800 focus:bg-white transition" onchange="autoPreencherAluno(this)">
                                    <option value="">-- Selecione para preencher como Aluno --</option>
                                    {% for cand in candidatos_batismo %}
                                    <option value="{{ cand['id'] }}" data-nome="{{ cand['nome'] }}">{{ cand['nome'] }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <input type="hidden" name="membro_id" id="input_membro_id" value="">
                            <input type="text" name="usuario" id="input_usuario" required placeholder="Login (ex: amunguambe) *" class="w-full h-11 px-3 text-sm border-2 rounded-xl font-semibold">
                            <input type="password" name="senha" required placeholder="Palavra-passe *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            
                            <select name="cargo" id="select_cargo" required class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white font-bold text-blue-950">
                                <option value="Secretário">Secretário (Cadastro & Atos)</option>
                                <option value="Líder">Líder de Ministério</option>
                                <option value="Tesoureiro">Tesoureiro (Tesouraria & Dashboard)</option>
                                <option value="Estudante">Estudante (Apenas Área de Estudos)</option>
                                <option value="Pastor">Pastor (Administrador Geral)</option>
                            </select>
                            <button type="submit" class="w-full h-12 bg-emerald-700 hover:bg-emerald-800 text-white font-black text-sm rounded-2xl shadow transition">Criar Utilizador</button>
                        </form>

                        <script>
                        function normalizarTexto(txt) {
                            return txt.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]/g, '');
                        }

                        function autoPreencherAluno(sel) {
                            var opt = sel.options[sel.selectedIndex];
                            var nome = opt.getAttribute('data-nome');
                            var id = opt.value;
                            if (nome && id) {
                                document.getElementById('input_membro_id').value = id;
                                var partes = nome.trim().split(/\\s+/);
                                var loginGerado = "";
                                if (partes.length === 1) {
                                    loginGerado = normalizarTexto(partes[0]);
                                } else {
                                    var primLetra = normalizarTexto(partes[0].charAt(0));
                                    var ultSobrenome = normalizarTexto(partes[partes.length - 1]);
                                    loginGerado = primLetra + ultSobrenome;
                                }
                                document.getElementById('input_usuario').value = loginGerado;
                                document.getElementById('select_cargo').value = 'Estudante';
                            } else {
                                document.getElementById('input_membro_id').value = '';
                            }
                        }
                        </script>"""

if 'action="/usuarios/novo"' in dash:
    dash = re.sub(
        r'<form action="/usuarios/novo" method="POST" class="space-y-3">.*?</form>',
        bloco_form_novo,
        dash,
        flags=re.DOTALL
    )
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dash)
    print("✓ templates/dashboard.html atualizado com seletor de Candidatos e auto-geração de login!")

# 2. Atualizar app.py para fornecer candidatos_batismo ao dashboard e salvar membro_id na tabela usuarios
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Consulta dos candidatos ao batismo na rota dashboard
alvo_dashboard = "return render_template('dashboard.html', planos=planos,"
injecao_candidatos = """    # Buscar Candidatos ao Batismo para matricula/criacao de usuario
    candidatos_batismo = []
    try:
        cur_cb = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur_cb.execute(\"\"\"
            SELECT id, nome FROM membros 
            WHERE LOWER(COALESCE(funcao, '')) LIKE '%candidat%' 
               OR LOWER(COALESCE(funcao, '')) LIKE '%prova%' 
               OR LOWER(COALESCE(funcao, '')) LIKE '%convertid%'
               OR LOWER(COALESCE(batizado, '')) IN ('nao', 'não', 'pendente', '')
               OR funcao IS NULL
            ORDER BY nome ASC
        \"\"\")
        candidatos_batismo = cur_cb.fetchall()
    except Exception as e:
        # Fallback: todos os membros
        try:
            cur_cb = conn.cursor() if hasattr(conn, 'cursor') else conn
            cur_cb.execute("SELECT id, nome FROM membros ORDER BY nome ASC")
            candidatos_batismo = cur_cb.fetchall()
        except Exception:
            pass

    return render_template('dashboard.html', candidatos_batismo=candidatos_batismo, planos=planos,"""

if alvo_dashboard in app_code and "candidatos_batismo=candidatos_batismo" not in app_code:
    app_code = app_code.replace(alvo_dashboard, injecao_candidatos, 1)
    print("✓ app.py: candidatos_batismo injetado com sucesso na rota do dashboard!")

# Na rota /usuarios/novo, salvar com o membro_id
trecho_usuario_antigo = """    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    if user and senha:
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (user, senha, cargo))"""

trecho_usuario_novo = """    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    m_id_form = request.form.get('membro_id')
    m_id_val = int(m_id_form) if (m_id_form and m_id_form.isdigit()) else None

    if user and senha:
        conn = get_db()
        try:
            # Garante que a coluna membro_id existe na tabela usuarios
            try:
                conn.execute("ALTER TABLE usuarios ADD COLUMN membro_id INTEGER")
                conn.commit()
            except Exception:
                pass

            param_char = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            if m_id_val:
                conn.execute(f"INSERT INTO usuarios (usuario, senha, cargo, membro_id) VALUES ({param_char}, {param_char}, {param_char}, {param_char})", (user, senha, cargo, m_id_val))
            else:
                conn.execute(f"INSERT INTO usuarios (usuario, senha, cargo) VALUES ({param_char}, {param_char}, {param_char})", (user, senha, cargo))"""

if "user = (request.form.get('usuario') or '').strip()" in app_code and "m_id_form = request.form.get('membro_id')" not in app_code:
    app_code = app_code.replace(trecho_usuario_antigo, trecho_usuario_novo)
    print("✓ app.py: rota /usuarios/novo atualizada para registrar membro_id!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✓ Processo concluído com êxito!")