import os
import re

# 1. Procurar o ficheiro do logótipo em static
caminho_logo = "/static/logo.png"
if os.path.exists("static"):
    for root, dirs, files in os.walk("static"):
        for f in files:
            if any(term in f.lower() for term in ["logo", "emblema", "iead"]):
                caminho_rel = os.path.relpath(os.path.join(root, f), ".").replace("\\", "/")
                caminho_logo = "/" + caminho_rel
                break

print(f"-> Logotipo selecionado: {caminho_logo}")

# 2. Atualizar templates/censo_form.html com o Logótipo oficial
with open("templates/censo_form.html", "r", encoding="utf-8") as f:
    form_html = f.read()

# Substituir o bloco do ícone ou imagem antiga pelo logótipo oficial com fundo circular
cabecalho_antigo = re.search(r'<header[\s\S]*?</header>', form_html)
novo_cabecalho = f"""<header class="bg-slate-900 text-white py-6 px-4 text-center shadow-lg sticky top-0 z-30 border-b-2 border-emerald-600">
        <div class="flex justify-center mb-3">
            <div class="w-20 h-20 bg-white p-2 rounded-2xl shadow-md border-2 border-emerald-500/40 flex items-center justify-center">
                <img src="{caminho_logo}" alt="IEAD Chicuque" class="max-h-full max-w-full object-contain">
            </div>
        </div>
        <h1 class="text-xl font-black uppercase tracking-wider text-white">IEAD CHICUQUE</h1>
        <p class="text-xs text-emerald-300 font-medium tracking-wide">Gestão Eclesiástica Integrada &bull; Ficha Oficial de Recenseamento</p>
    </header>"""

if cabecalho_antigo:
    form_html = form_html.replace(cabecalho_antigo.group(0), novo_cabecalho)
    with open("templates/censo_form.html", "w", encoding="utf-8") as f:
        f.write(form_html)
    print("✓ templates/censo_form.html atualizado com o Logótipo oficial!")

# 3. Atualizar a rota /censo no app.py com criação garantida de colunas em tempo de execução
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

rota_auto_reparavel = """
@app.route('/censo', methods=['GET', 'POST'])
def censo_publico():
    msg_erro = None
    igreja_param = request.args.get('igreja', 'IEAD Chicuque')
    
    # 1. Garantir que as colunas críticas existam imediatamente
    colunas_obrigatorias = [
        ("igreja", "TEXT"),
        ("batizado", "TEXT"),
        ("data_batismo", "TEXT"),
        ("endereco", "TEXT"),
        ("bairro", "TEXT"),
        ("naturalidade", "TEXT"),
        ("filiacao", "TEXT"),
        ("tipo_doc", "TEXT"),
        ("num_doc", "TEXT"),
        ("segmento", "TEXT"),
        ("ano_conversao", "TEXT"),
        ("cargo", "TEXT"),
        ("departamento", "TEXT"),
        ("status", "TEXT"),
        ("foto_path", "TEXT"),
        ("professor_nome", "TEXT")
    ]
    
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = bool(DATABASE_URL and psycopg2)
    
    for col, tipo in colunas_obrigatorias:
        try:
            if is_pg:
                cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
            else:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            conn.commit()
        except Exception:
            if is_pg:
                conn.rollback()

    # Buscar lista de congregações
    lista_igrejas = ['IEAD Chicuque']
    try:
        cur.execute("SELECT nome FROM igrejas ORDER BY nome ASC")
        rows = cur.fetchall()
        if rows:
            lista_igrejas = [r[0] for r in rows if r[0]]
            if 'IEAD Chicuque' not in lista_igrejas:
                lista_igrejas.insert(0, 'IEAD Chicuque')
    except Exception:
        pass

    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        telefone = (request.form.get('telefone') or '').strip()
        igreja_escolhida = request.form.get('igreja') or igreja_param
        
        if not nome or not telefone:
            msg_erro = "Por favor, preencha o Nome Completo e o Contacto telefónico."
            if hasattr(conn, 'close'):
                conn.close()
            return render_template('censo_form.html', msg_erro=msg_erro, igrejas=lista_igrejas, igreja_selecionada=igreja_param)
            
        foto_path = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                nome_foto = f"membro_{int(time.time())}.{ext}"
                caminho_salvar = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), nome_foto)
                os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
                file.save(caminho_salvar)
                foto_path = f"/static/uploads/{nome_foto}"

        campos = {
            'nome': nome,
            'telefone': telefone,
            'igreja': igreja_escolhida,
            'data_nascimento': request.form.get('data_nascimento'),
            'genero': request.form.get('genero'),
            'estado_civil': request.form.get('estado_civil'),
            'bairro': request.form.get('bairro'),
            'endereco': request.form.get('endereco') or request.form.get('bairro'),
            'naturalidade': request.form.get('naturalidade'),
            'filiacao': request.form.get('filiacao'),
            'tipo_doc': request.form.get('tipo_doc'),
            'num_doc': request.form.get('num_doc'),
            'segmento': request.form.get('segmento'),
            'ano_conversao': request.form.get('ano_conversao'),
            'batizado': request.form.get('batizado', 'Não'),
            'cargo': request.form.get('cargo', 'Membro em Comunhão'),
            'departamento': request.form.get('departamento', 'Geral'),
            'status': 'Pendente de Validação',
            'foto_path': foto_path,
            'professor_nome': session.get('usuario', 'Auto-recenseamento')
        }

        try:
            # Obter lista de colunas ativas na tabela
            if is_pg:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'membros';")
                cols_db = [r[0].lower() for r in cur.fetchall()]
            else:
                cur.execute("PRAGMA table_info(membros);")
                cols_db = [r[1].lower() for r in cur.fetchall()]
                
            cols_inserir = [k for k in campos.keys() if k.lower() in cols_db]
            vals_inserir = [campos[k] for k in cols_inserir]
            
            param = "%s" if is_pg else "?"
            sql = f"INSERT INTO membros ({', '.join(cols_inserir)}) VALUES ({', '.join([param]*len(cols_inserir))})"
            cur.execute(sql, tuple(vals_inserir))
            conn.commit()
            if hasattr(conn, 'close'):
                conn.close()
            return render_template('censo_sucesso.html', nome=nome, status='Pendente de Validação', igreja=igreja_escolhida)
        except Exception as e:
            msg_erro = f"Erro ao registar a ficha: {e}"

    if hasattr(conn, 'close'):
        conn.close()
    return render_template('censo_form.html', msg_erro=msg_erro, igrejas=lista_igrejas, igreja_selecionada=igreja_param)
"""

padrao = r"@app\.route\('/censo'[\s\S]*?return render_template\('censo_form\.html'[\s\S]*?\)"
if re.search(padrao, code):
    code = re.sub(padrao, rota_auto_reparavel.strip(), code)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✓ Rota /censo atualizada com reparação de colunas em tempo real!")
else:
    print("Aviso: Rota anterior não localizada.")