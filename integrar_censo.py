import os

# 1. ATUALIZAR APP.PY COM AS ROTAS DO CENSO
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

rotas_censo = """
# =======================================================
# MÓDULO DE CENSO E AUTO-RECENSEAMENTO (PÚBLICO & BRIGADAS)
# =======================================================
import os
from werkzeug.utils import secure_filename

@app.route('/censo', methods=['GET', 'POST'])
def censo_publico():
    msg_erro = None
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        data_nascimento = request.form.get('data_nascimento')
        genero = request.form.get('genero')
        estado_civil = request.form.get('estado_civil')
        telefone = (request.form.get('telefone') or '').strip()
        bairro = request.form.get('bairro')
        endereco = request.form.get('endereco')
        profissao = request.form.get('profissao')
        batizado = request.form.get('batizado', 'Não')
        data_batismo = request.form.get('data_batismo')
        departamento = request.form.get('departamento')
        funcao = request.form.get('funcao', 'Membro')
        
        # Identificação de quem registou (Se for brigada logada ou público)
        recenseador = session.get('usuario', 'Auto-recenseamento (WhatsApp)')
        
        if not nome or not telefone:
            msg_erro = "Por favor, preencha o Nome Completo e o Contacto telefónico."
            return render_template('censo_form.html', msg_erro=msg_erro)
            
        foto_path = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                nome_foto = f"membro_{int(time.time())}.{ext}"
                caminho_salvar = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), nome_foto)
                file.save(caminho_salvar)
                foto_path = f"/static/uploads/{nome_foto}"

        try:
            conn = get_db()
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
            
            # Se for feito por membro online, fica como 'Pendente de Validação'
            # Se for cadastrado por uma brigada/pastor logado, entra direto como 'Ativo'
            status_inicial = 'Ativo' if session.get('usuario') else 'Pendente de Validação'
            
            sql = f'''
                INSERT INTO membros (
                    nome, data_nascimento, genero, estado_civil, telefone,
                    bairro, endereco, profissao, batizado, data_batismo,
                    departamento, funcao, status, foto_path, professor_nome
                ) VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})
            '''
            cur.execute(sql, (
                nome, data_nascimento, genero, estado_civil, telefone,
                bairro, endereco, profissao, batizado, data_batismo,
                departamento, funcao, status_inicial, foto_path, recenseador
            ))
            conn.commit()
            if hasattr(conn, 'close'):
                conn.close()
                
            return render_template('censo_sucesso.html', nome=nome, status=status_inicial)
        except Exception as e:
            msg_erro = f"Erro ao registar a ficha: {e}"

    return render_template('censo_form.html', msg_erro=msg_erro)


@app.route('/admin/censo/homologar')
def painel_homologacao_censo():
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    
    cur.execute(f"SELECT id, nome, telefone, bairro, batizado, departamento, foto_path, professor_nome, data_cadastro FROM membros WHERE status = {param} ORDER BY id DESC", ('Pendente de Validação',))
    pendentes = cur.fetchall()
    if hasattr(conn, 'close'):
        conn.close()
        
    return render_template('censo_homologar.html', pendentes=pendentes)


@app.route('/admin/censo/aprovar/<int:membro_id>', methods=['POST'])
def aprovar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"UPDATE membros SET status = {param} WHERE id = {param}", ('Ativo', membro_id))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')


@app.route('/admin/censo/descartar/<int:membro_id>', methods=['POST'])
def descartar_censo(membro_id):
    if not session.get('usuario'):
        return redirect('/login')
        
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
    cur.execute(f"DELETE FROM membros WHERE id = {param}", (membro_id,))
    conn.commit()
    if hasattr(conn, 'close'):
        conn.close()
    return redirect('/admin/censo/homologar')
"""

if '/censo' not in app_code:
    app_code += "\n" + rotas_censo
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("✓ Rotas do censo adicionadas ao app.py!")
else:
    print("As rotas do censo já existem no app.py.")

# 2. CRIAR TEMPLATE templates/censo_form.html (OTIMIZADO PARA ANDROID/MOBILE)
html_censo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Censo Oficial - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-100 min-h-screen text-slate-800">
    <header class="bg-blue-950 text-white py-6 px-4 text-center shadow-lg sticky top-0 z-30">
        <div class="inline-block p-3 bg-white/10 rounded-2xl mb-2 backdrop-blur-sm">
            <i class="fa-solid fa-church text-3xl text-amber-400"></i>
        </div>
        <h1 class="text-xl font-black uppercase tracking-wider">IEAD Chicuque</h1>
        <p class="text-xs text-blue-200 mt-1 font-medium">Ficha Oficial de Recenseamento de Membros</p>
    </header>

    <main class="max-w-lg mx-auto p-4 sm:p-6 pb-20">
        {% if msg_erro %}
        <div class="mb-4 p-4 bg-rose-50 border-l-4 border-rose-600 text-rose-800 text-xs rounded-xl shadow-sm font-bold flex items-center gap-3">
            <i class="fa-solid fa-circle-exclamation text-base text-rose-600"></i>
            <span>{{ msg_erro }}</span>
        </div>
        {% endif %}

        <div class="bg-white rounded-3xl p-6 shadow-sm border border-slate-200">
            <form action="/censo" method="POST" enctype="multipart/form-data" class="space-y-5">
                
                <!-- Secção 1: Identificação -->
                <div>
                    <h2 class="text-xs font-black uppercase tracking-wider text-blue-900 border-b pb-2 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-user text-amber-500"></i> Dados Pessoais
                    </h2>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Nome Completo *</label>
                            <input type="text" name="nome" required placeholder="Ex: Lucas Manuel" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Data Nascimento</label>
                                <input type="date" name="data_nascimento" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Género</label>
                                <select name="genero" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                                    <option value="Masculino">Masculino</option>
                                    <option value="Feminino">Feminino</option>
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Estado Civil</label>
                                <select name="estado_civil" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                                    <option value="Solteiro(a)">Solteiro(a)</option>
                                    <option value="Casado(a)">Casado(a)</option>
                                    <option value="Viúvo(a)">Viúvo(a)</option>
                                    <option value="Divorciado(a)">Divorciado(a)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Profissão</label>
                                <input type="text" name="profissao" placeholder="Ex: Professor" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Secção 2: Contacto e Localização -->
                <div class="pt-2">
                    <h2 class="text-xs font-black uppercase tracking-wider text-blue-900 border-b pb-2 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-phone text-amber-500"></i> Contactos & Bairro
                    </h2>

                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Telefone / WhatsApp *</label>
                            <input type="tel" name="telefone" required placeholder="84... / 82..." class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none font-semibold">
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Bairro</label>
                                <input type="text" name="bairro" placeholder="Ex: Chicuque" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Quarteirão / Rua</label>
                                <input type="text" name="endereco" placeholder="Q. 04 / Casa 12" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Secção 3: Vida Eclesiástica -->
                <div class="pt-2">
                    <h2 class="text-xs font-black uppercase tracking-wider text-blue-900 border-b pb-2 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-cross text-amber-500"></i> Informação Eclesiástica
                    </h2>

                    <div class="space-y-4">
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Batizado nas Águas?</label>
                                <select name="batizado" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                                    <option value="Sim">Sim</option>
                                    <option value="Não">Não</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Ano de Batismo</label>
                                <input type="text" name="data_batismo" placeholder="Ex: 2021" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                            </div>
                        </div>

                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Departamento / Ministério</label>
                            <select name="departamento" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
                                <option value="Geral">Membro Geral</option>
                                <option value="Jovens">Mocidade / Jovens</option>
                                <option value="Senhoras">Senhoras (MIFED)</option>
                                <option value="Homens">Homens (MIFED)</option>
                                <option value="Louvor">Louvor / Música</option>
                                <option value="Diaconato">Diaconato / Acolhimento</option>
                                <option value="Criancas">Escola Bíblica Infantil</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Fotografia Tipo Passe (Opcional)</label>
                            <input type="file" name="foto" accept="image/*" capture="user" class="w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-black file:bg-blue-50 file:text-blue-900 hover:file:bg-blue-100">
                            <p class="text-[10px] text-slate-400 mt-1">Pode tirar uma selfie na hora com a câmara do telemóvel.</p>
                        </div>
                    </div>
                </div>

                <button type="submit" class="w-full h-14 bg-blue-900 hover:bg-blue-950 text-white font-black text-sm uppercase tracking-wider rounded-2xl shadow-xl transition flex items-center justify-center gap-2 mt-6">
                    <i class="fa-solid fa-paper-plane"></i> Submeter Ficha de Membro
                </button>
            </form>
        </div>
    </main>
</body>
</html>
"""
with open('templates/censo_form.html', 'w', encoding='utf-8') as f:
    f.write(html_censo)
print("✓ Template templates/censo_form.html criado!")

# 3. CRIAR TEMPLATE templates/censo_sucesso.html
html_sucesso = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registo Concluído - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl p-8 text-center shadow-2xl border border-slate-100">
        <div class="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
            <i class="fa-solid fa-check"></i>
        </div>
        <h1 class="text-2xl font-black text-slate-900">Glória a Deus!</h1>
        <p class="text-sm font-bold text-blue-900 mt-2">Paz do Senhor, {{ nome }}!</p>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
            A sua ficha de recenseamento foi enviada com sucesso para a <b>Secretaria Geral da IEAD Chicuque</b>.
        </p>
        
        <div class="mt-8 border-t pt-4">
            <a href="/censo" class="inline-block w-full py-3 bg-blue-900 text-white text-xs font-black rounded-xl shadow-md hover:bg-blue-950 transition">
                Registar Outro Familiar
            </a>
        </div>
    </div>
</body>
</html>
"""
with open('templates/censo_sucesso.html', 'w', encoding='utf-8') as f:
    f.write(html_sucesso)
print("✓ Template templates/censo_sucesso.html criado!")

# 4. CRIAR TEMPLATE templates/censo_homologar.html (PAINEL DA SECRETARIA)
html_homologar = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homologação do Censo - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-100 min-h-screen">
    <div class="max-w-6xl mx-auto p-4 sm:p-6">
        <div class="flex items-center justify-between mb-6">
            <div>
                <h1 class="text-2xl font-black text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-clipboard-check text-blue-900"></i> Fichas do Censo para Validação
                </h1>
                <p class="text-xs text-slate-500">Membros cadastrados via link público aguardando confirmação</p>
            </div>
            <a href="/" class="bg-slate-800 text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-slate-900">
                ← Voltar ao Painel
            </a>
        </div>

        {% if pendentes %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {% for m in pendentes %}
            <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <div class="flex items-center gap-3 mb-3">
                        {% if m[6] %}
                        <img src="{{ m[6] }}" class="w-12 h-12 rounded-full object-cover border">
                        {% else %}
                        <div class="w-12 h-12 rounded-full bg-blue-100 text-blue-900 font-bold flex items-center justify-center">
                            {{ m[1][:2].upper() }}
                        </div>
                        {% endif %}
                        <div>
                            <h3 class="font-bold text-slate-900 text-sm leading-tight">{{ m[1] }}</h3>
                            <span class="text-[10px] text-slate-500 block">📞 {{ m[2] }}</span>
                        </div>
                    </div>

                    <div class="text-xs space-y-1 text-slate-600 bg-slate-50 p-3 rounded-xl mb-4">
                        <p><b>Bairro:</b> {{ m[3] or 'Não informado' }}</p>
                        <p><b>Batizado:</b> {{ m[4] }}</p>
                        <p><b>Departamento:</b> {{ m[5] or 'Geral' }}</p>
                        <p class="text-[10px] text-blue-900 font-bold">Origem: {{ m[7] }}</p>
                    </div>
                </div>

                <div class="flex gap-2 pt-2 border-t">
                    <form action="/admin/censo/aprovar/{{ m[0] }}" method="POST" class="flex-1">
                        <button type="submit" class="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1">
                            <i class="fa-solid fa-check"></i> Homologar
                        </button>
                    </form>
                    <form action="/admin/censo/descartar/{{ m[0] }}" method="POST">
                        <button type="submit" onclick="return confirm('Deseja descartar este registo?')" class="px-3 py-2 bg-rose-50 text-rose-600 hover:bg-rose-100 rounded-xl text-xs font-bold transition">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="bg-white rounded-3xl p-12 text-center border border-slate-200 shadow-sm">
            <i class="fa-solid fa-circle-check text-4xl text-emerald-500 mb-3"></i>
            <h2 class="text-base font-bold text-slate-800">Tudo em dia!</h2>
            <p class="text-xs text-slate-500 mt-1">Não existem fichas pendentes de validação no momento.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""
with open('templates/censo_homologar.html', 'w', encoding='utf-8') as f:
    f.write(html_homologar)
print("✓ Template templates/censo_homologar.html criado!")