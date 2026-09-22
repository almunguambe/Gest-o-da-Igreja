with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Rota para o professor/pastor responder à dúvida bíblica
rota_responder_duvida = '''
@app.route('/discipulado/responder_duvida/<int:id>', methods=['POST'])
def responder_duvida_discipulado(id):
    from flask import request, redirect
    resposta = request.form.get('resposta', '').strip()
    if resposta:
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                UPDATE duvidas_discipulado 
                SET resposta = %s 
                WHERE id = %s
            """ if DATABASE_URL and psycopg2 else """
                UPDATE duvidas_discipulado 
                SET resposta = ? 
                WHERE id = ?
            """, (resposta, id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao salvar resposta: {e}")
    return redirect('/#secao-discipulado')
'''

if "def responder_duvida_discipulado(" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", rota_responder_duvida + "\nif __name__ ==")
    else:
        conteudo += "\n" + rota_responder_duvida

# 2. Injetar dúvidas e notas de progresso no contexto da rota principal index / dashboard
codigo_contexto_dashboard = '''
        # Carregar dúvidas bíblicas para o painel pastoral
        duvidas_lista = []
        candidatos_discipulado = []
        try:
            c.execute("SELECT * FROM duvidas_discipulado ORDER BY id DESC LIMIT 20")
            duvidas_lista = c.fetchall()
        except Exception:
            pass

        try:
            query_prog = """
                SELECT m.id, m.nome, m.foto_path, m.telefone,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c1' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c1_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c2' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c2_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c3' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c3_ok,
                       COALESCE(MAX(CASE WHEN p.classe_id = 'c4' AND p.status = 'Aprovado' THEN 1 ELSE 0 END), 0) as c4_ok
                FROM membros m
                LEFT JOIN progresso_discipulado p ON m.id = p.membro_id
                GROUP BY m.id, m.nome, m.foto_path, m.telefone
                ORDER BY m.id DESC
            """
            c.execute(query_prog)
            candidatos_discipulado = c.fetchall()
        except Exception:
            pass
'''

# Se encontrar render_template('dashboard.html', adiciona os dados extras
if "render_template('dashboard.html'" in conteudo:
    conteudo = conteudo.replace(
        "render_template('dashboard.html',",
        "render_template('dashboard.html', duvidas=duvidas_lista, discipulado_alunos=candidatos_discipulado,"
    )
    # Adiciona a coleta logo antes de fechar a conexão ou renderizar
    if "return render_template('dashboard.html'" in conteudo:
        partes = conteudo.split("return render_template('dashboard.html'")
        conteudo = partes[0] + codigo_contexto_dashboard + "\n        return render_template('dashboard.html'" + partes[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Rotas de dúvidas e mapeamento de progresso configurados no app.py!")