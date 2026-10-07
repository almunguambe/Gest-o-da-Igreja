with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Atualizar o início das consultas no dashboard para obter o igreja_id e filtrar
trecho_inicio = """    conn = get_db()
    total_membros = conn.execute("SELECT COUNT(*) FROM membros").fetchone()[0]
    total_casamentos = conn.execute("SELECT COUNT(*) FROM casamentos").fetchone()[0]
    total_mortes = conn.execute("SELECT COUNT(*) FROM mortes").fetchone()[0]

    entrada_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saida_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)").fetchone()[0] or 0.0
    saldo_caixa = entrada_caixa - saida_caixa

    entrada_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saida_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND local_movimento = 'Banco'").fetchone()[0] or 0.0
    saldo_banco = entrada_banco - saida_banco
    saldo_total = (entrada_caixa + entrada_banco) - (saida_caixa + saida_banco)

    hoje_md = datetime.now().strftime("-%m-%d")
    aniversariantes_dia = conn.execute("SELECT nome, data_nascimento, telefone, departamento FROM membros WHERE data_nascimento LIKE ?", (f"%{hoje_md}",)).fetchall()"""

novo_inicio = """    conn = get_db()
    
    # Contexto Multi-Igreja
    is_super = session.get('is_superadmin', False)
    req_igreja = request.args.get('igreja_id', type=int)
    if is_super and req_igreja:
        igreja_id = req_igreja
        session['igreja_id'] = igreja_id
        ig_row = conn.execute("SELECT nome FROM igrejas WHERE id = ?", (igreja_id,)).fetchone()
        if ig_row:
            session['igreja_nome'] = ig_row['nome']
    else:
        igreja_id = session.get('igreja_id', 1)

    lista_igrejas = conn.execute("SELECT * FROM igrejas WHERE ativa = 1 ORDER BY nome ASC").fetchall() if is_super else []

    total_membros = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]
    total_casamentos = conn.execute("SELECT COUNT(*) FROM casamentos WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]
    total_mortes = conn.execute("SELECT COUNT(*) FROM mortes WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]

    entrada_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Entrada' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)", (igreja_id,)).fetchone()[0] or 0.0
    saida_caixa = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Saída' AND (local_movimento = 'Caixa' OR local_movimento IS NULL)", (igreja_id,)).fetchone()[0] or 0.0
    saldo_caixa = entrada_caixa - saida_caixa

    entrada_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Entrada' AND local_movimento = 'Banco'", (igreja_id,)).fetchone()[0] or 0.0
    saida_banco = conn.execute("SELECT SUM(valor) FROM financeiro WHERE igreja_id = ? AND tipo = 'Saída' AND local_movimento = 'Banco'", (igreja_id,)).fetchone()[0] or 0.0
    saldo_banco = entrada_banco - saida_banco
    saldo_total = (entrada_caixa + entrada_banco) - (saida_caixa + saida_banco)

    hoje_md = datetime.now().strftime("-%m-%d")
    aniversariantes_dia = conn.execute("SELECT nome, data_nascimento, telefone, departamento FROM membros WHERE igreja_id = ? AND data_nascimento LIKE ?", (igreja_id, f"%{hoje_md}")).fetchall()"""

if trecho_inicio in code:
    code = code.replace(trecho_inicio, novo_inicio, 1)
    print("✓ Início do dashboard filtrado por igreja_id!")

# 2. Filtrar as listagens de membros, finanças, etc.
trecho_listas = """    todos_membros = conn.execute("SELECT * FROM membros ORDER BY id DESC").fetchall()
    todas_financas = conn.execute("SELECT * FROM financeiro ORDER BY id DESC").fetchall()
    todos_casamentos = conn.execute("SELECT * FROM casamentos ORDER BY id DESC").fetchall()
    todas_mortes = conn.execute("SELECT * FROM mortes ORDER BY id DESC").fetchall()
    todos_cultos = conn.execute("SELECT * FROM cultos_frequencia ORDER BY id DESC LIMIT 25").fetchall()
    todos_convertidos = conn.execute("SELECT * FROM novos_convertidos ORDER BY id DESC").fetchall()
    todo_patrimonio = conn.execute("SELECT * FROM patrimonio ORDER BY departamento, item ASC").fetchall()
    todas_escalas = conn.execute("SELECT * FROM escalas ORDER BY data_escala DESC LIMIT 20").fetchall()
    lista_usuarios = conn.execute("SELECT id, usuario, cargo FROM usuarios ORDER BY id ASC").fetchall()
    ultimas_transferencias = conn.execute("SELECT * FROM transferencias ORDER BY id DESC LIMIT 20").fetchall()"""

novo_listas = """    todos_membros = conn.execute("SELECT * FROM membros WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todas_financas = conn.execute("SELECT * FROM financeiro WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todos_casamentos = conn.execute("SELECT * FROM casamentos WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todas_mortes = conn.execute("SELECT * FROM mortes WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todos_cultos = conn.execute("SELECT * FROM cultos_frequencia WHERE igreja_id = ? ORDER BY id DESC LIMIT 25", (igreja_id,)).fetchall()
    todos_convertidos = conn.execute("SELECT * FROM novos_convertidos WHERE igreja_id = ? ORDER BY id DESC", (igreja_id,)).fetchall()
    todo_patrimonio = conn.execute("SELECT * FROM patrimonio WHERE igreja_id = ? ORDER BY departamento, item ASC", (igreja_id,)).fetchall()
    todas_escalas = conn.execute("SELECT * FROM escalas WHERE igreja_id = ? ORDER BY data_escala DESC LIMIT 20", (igreja_id,)).fetchall()
    lista_usuarios = conn.execute("SELECT id, usuario, cargo FROM usuarios WHERE igreja_id = ? ORDER BY id ASC", (igreja_id,)).fetchall()
    ultimas_transferencias = conn.execute("SELECT * FROM transferencias WHERE igreja_id = ? ORDER BY id DESC LIMIT 20", (igreja_id,)).fetchall()"""

if trecho_listas in code:
    code = code.replace(trecho_listas, novo_listas, 1)
    print("✓ Listas do dashboard filtradas por igreja_id!")

# 3. Adicionar lista_igrejas ao retorno do render_template
if "lista_igrejas=lista_igrejas," not in code:
    code = code.replace("todos_membros=todos_membros,", "todos_membros=todos_membros,\n                           lista_igrejas=lista_igrejas if 'lista_igrejas' in locals() else [],", 1)
    print("✓ lista_igrejas injetada no render_template!")

# 4. Adicionar as rotas do SuperAdmin no final do arquivo app.py se ainda não existirem
rotas_superadmin = '''
# ==========================================================
# ROTAS SUPERADMIN (GESTAO DE TODAS AS IGREJAS)
# ==========================================================
@app.route('/superadmin/igrejas', methods=['GET', 'POST'])
def superadmin_igrejas():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito ao Super Administrador.", "erro")
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        cidade = (request.form.get('cidade') or '').strip()
        distrito = (request.form.get('distrito') or '').strip()
        pastor = (request.form.get('pastor') or '').strip()
        telefone = (request.form.get('telefone') or '').strip()
        
        # Dados do primeiro utilizador da congregação
        admin_user = (request.form.get('admin_user') or '').strip()
        admin_pass = (request.form.get('admin_pass') or '').strip()
        
        if nome:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO igrejas (nome, cidade, distrito, pastor, telefone, ativa)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (nome, cidade, distrito, pastor, telefone))
                nova_igreja_id = cur.lastrowid
                
                if admin_user and admin_pass:
                    cur.execute("""
                        INSERT INTO usuarios (usuario, senha, cargo, igreja_id, is_superadmin)
                        VALUES (?, ?, 'Pastor', ?, 0)
                    """, (admin_user, admin_pass, nova_igreja_id))
                
                conn.commit()
                flash(f"Congregação '{nome}' criada com sucesso!", "sucesso")
            except Exception as e:
                flash(f"Erro ao criar congregação: {e}", "erro")
        return redirect(url_for('superadmin_igrejas'))
        
    igrejas = conn.execute("""
        SELECT i.*, 
               (SELECT COUNT(*) FROM membros m WHERE m.igreja_id = i.id) as total_membros,
               (SELECT COUNT(*) FROM usuarios u WHERE u.igreja_id = i.id) as total_usuarios
        FROM igrejas i
        ORDER BY i.id ASC
    """).fetchall()
    conn.close()
    return render_template('superadmin_igrejas.html', igrejas=igrejas)
'''

if "/superadmin/igrejas" not in code:
    code = code + "\n" + rotas_superadmin
    print("✓ Rotas de SuperAdmin adicionadas ao app.py!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("--- APLICACAO CONCLUIDA COM SUCESSO! ---")