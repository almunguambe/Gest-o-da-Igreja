# 1. Substituir linhas 1654 a 1665 em templates/dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

novo_form = """                        <form action="/usuarios/novo" method="POST" class="space-y-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Candidato ao Batismo (Aluno de Discipulado):</label>
                                <select id="select_candidato_membro" class="w-full h-11 px-2 text-sm border-2 border-indigo-200 rounded-xl bg-indigo-50/60 font-semibold text-indigo-950 focus:bg-white" onchange="autoPreencherAluno(this)">
                                    <option value="">-- Selecione para preencher como Aluno --</option>
                                    {% for cand in candidatos_batismo %}
                                    <option value="{{ cand['id'] if cand is mapping else cand[0] }}" data-nome="{{ cand['nome'] if cand is mapping else cand[1] }}">{{ cand['nome'] if cand is mapping else cand[1] }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <input type="hidden" name="membro_id" id="input_membro_id" value="">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Nome de Utilizador / Login *</label>
                                <input type="text" name="usuario" id="input_usuario" required placeholder="Login (ex: amunguambe)" class="w-full h-11 px-3 text-sm border-2 rounded-xl font-bold text-slate-800">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Palavra-passe *</label>
                                <input type="password" name="senha" required placeholder="Palavra-passe *" class="w-full h-11 px-3 text-sm border-2 rounded-xl">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Nível de Permissão *</label>
                                <select name="cargo" id="select_cargo" required class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white font-bold text-blue-950">
                                    <option value="Secretário">Secretário (Cadastro & Atos)</option>
                                    <option value="Líder">Líder de Ministério</option>
                                    <option value="Tesoureiro">Tesoureiro (Tesouraria & Dashboard)</option>
                                    <option value="Estudante">Estudante (Apenas Área de Estudos)</option>
                                    <option value="Pastor">Pastor (Administrador Geral)</option>
                                </select>
                            </div>
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
                        </script>
"""

# Localizar exatamente onde comeca <form action="/usuarios/novo"
idx_inicio = -1
idx_fim = -1
for i, l in enumerate(linhas):
    if '<form action="/usuarios/novo"' in l:
        idx_inicio = i
    if idx_inicio != -1 and '</form>' in l:
        idx_fim = i
        break

if idx_inicio != -1 and idx_fim != -1:
    linhas[idx_inicio:idx_fim+1] = [novo_form]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print(f"✓ templates/dashboard.html atualizado nas linhas {idx_inicio+1} a {idx_fim+1}!")
else:
    print("⚠️ Não foi possível determinar o início e fim do form.")

# 2. Assegurar que app.py passa candidatos_batismo e recebe membro_id
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Passagem de candidatos_batismo no render do dashboard
if "candidatos_batismo=candidatos_batismo" not in app_code:
    alvo = "return render_template('dashboard.html', planos=planos,"
    subst = """    # Buscar Candidatos ao Batismo para a tela de usuarios
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
    except Exception:
        try:
            cur_cb = conn.cursor() if hasattr(conn, 'cursor') else conn
            cur_cb.execute("SELECT id, nome FROM membros ORDER BY nome ASC")
            candidatos_batismo = cur_cb.fetchall()
        except Exception:
            pass

    return render_template('dashboard.html', candidatos_batismo=candidatos_batismo, planos=planos,"""
    app_code = app_code.replace(alvo, subst, 1)

# Gravacao de membro_id na rota /usuarios/novo
trecho_antigo = """    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    if user and senha:
        conn = get_db()
        try:
            conn.execute("INSERT INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)", (user, senha, cargo))"""

trecho_novo = """    user = (request.form.get('usuario') or '').strip()
    senha = (request.form.get('senha') or '').strip()
    cargo = (request.form.get('cargo') or '').strip()
    m_id_form = request.form.get('membro_id')
    m_id_val = int(m_id_form) if (m_id_form and m_id_form.isdigit()) else None

    if user and senha:
        conn = get_db()
        try:
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

if "m_id_form = request.form.get('membro_id')" not in app_code and "user = (request.form.get('usuario') or '').strip()" in app_code:
    app_code = app_code.replace(trecho_antigo, trecho_novo, 1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✓ app.py verificado e atualizado com sucesso!")