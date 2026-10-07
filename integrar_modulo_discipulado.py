with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

rotas_discipulado = """

# ================= ROTA DE GESTÃO DO FUNIL DE DISCIPULADO =================
@app.route('/discipulado/atualizar_fase', methods=['POST'])
def atualizar_fase_discipulado():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    membro_id = request.form.get('membro_id')
    nova_fase = request.form.get('nova_fase')
    discipulador = request.form.get('discipulador', '').strip()
    data_batismo = request.form.get('data_batismo', '').strip()
    
    conn = get_db()
    if nova_fase == 'Batizado' and data_batismo:
        conn.execute(\"\"\"
            UPDATE membros 
            SET fase_discipulado = ?, discipulador = COALESCE(NULLIF(?, ''), discipulador), data_batismo = ?
            WHERE id = ?
        \"\"\", (nova_fase, discipulador, data_batismo, membro_id))
    else:
        conn.execute(\"\"\"
            UPDATE membros 
            SET fase_discipulado = ?, discipulador = COALESCE(NULLIF(?, ''), discipulador)
            WHERE id = ?
        \"\"\", (nova_fase, discipulador, membro_id))
        
    conn.commit()
    conn.close()
    flash("Fase de discipulado atualizada com sucesso!", "sucesso")
    return redirect(url_for('dashboard') + "#secao-discipulado")
"""

if 'def atualizar_fase_discipulado' not in codigo:
    codigo += rotas_discipulado
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Rota /discipulado/atualizar_fase injetada com sucesso no app.py!")
else:
    print("! A rota de atualização de fase já existia no app.py.")