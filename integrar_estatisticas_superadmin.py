with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

rotas_estatisticas = """

@app.route('/superadmin/estatisticas')
def superadmin_estatisticas():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito ao Super Administrador.", "erro")
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    
    # Lista de igrejas com estatísticas consolidadas
    igrejas = conn.execute("SELECT * FROM igrejas ORDER BY id ASC").fetchall()
    stats_igrejas = []
    
    total_membros_geral = 0
    total_entradas_geral = 0.0
    total_saidas_geral = 0.0
    
    for ig in igrejas:
        ig_id = ig['id']
        membros_count = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (ig_id,)).fetchone()[0]
        entradas = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Entrada' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        saidas = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Saida' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        
        saldo = float(entradas) - float(saidas)
        total_membros_geral += membros_count
        total_entradas_geral += float(entradas)
        total_saidas_geral += float(saidas)
        
        stats_igrejas.append({
            'id': ig['id'],
            'nome': ig['nome'],
            'cidade': ig['cidade'],
            'distrito': ig['distrito'],
            'pastor': ig['pastor'],
            'telefone': ig['telefone'],
            'ativa': ig['ativa'],
            'total_membros': membros_count,
            'total_entradas': float(entradas),
            'total_saidas': float(saidas),
            'saldo': saldo
        })
        
    conn.close()
    
    saldo_geral = total_entradas_geral - total_saidas_geral
    
    return render_template(
        'superadmin_estatisticas.html',
        total_igrejas=len(igrejas),
        total_membros_geral=total_membros_geral,
        total_entradas_geral=total_entradas_geral,
        total_saidas_geral=total_saidas_geral,
        saldo_geral=saldo_geral,
        stats_igrejas=stats_igrejas
    )

@app.route('/superadmin/estatisticas/pdf')
def superadmin_estatisticas_pdf():
    if 'usuario' not in session or not session.get('is_superadmin'):
        flash("Acesso restrito.", "erro")
        return redirect(url_for('dashboard'))
        
    conn = get_db()
    igrejas = conn.execute("SELECT * FROM igrejas ORDER BY id ASC").fetchall()
    
    dados_tabela = [["Congregação", "Pastor Titular", "Membros", "Entradas (MT)", "Saídas (MT)", "Saldo (MT)"]]
    tot_membros = 0
    tot_ent = 0.0
    tot_sai = 0.0
    
    for ig in igrejas:
        ig_id = ig['id']
        m_cnt = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (ig_id,)).fetchone()[0]
        e = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Entrada' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        s = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'Saida' AND igreja_id = ?", (ig_id,)).fetchone()[0]
        sal = float(e) - float(s)
        
        tot_membros += m_cnt
        tot_ent += float(e)
        tot_sai += float(s)
        
        dados_tabela.append([
            ig['nome'][:20],
            (ig['pastor'] or '-')[:18],
            str(m_cnt),
            f"{float(e):,.2f}",
            f"{float(s):,.2f}",
            f"{sal:,.2f}"
        ])
    conn.close()
    
    # Linha Total
    dados_tabela.append([
        "TOTAL GERAL",
        "-",
        str(tot_membros),
        f"{tot_ent:,.2f}",
        f"{tot_sai:,.2f}",
        f"{(tot_ent - tot_sai):,.2f}"
    ])
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elementos = [
        Paragraph("<font color='#1e3a8a' size=14><b>IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS</b></font>", ParagraphStyle('H1', alignment=1)),
        Paragraph("<font size=10 color='#475569'><b>SISTEMA INTEGRADO DE GESTÃO ECLESIÁSTICA (SIGAD)</b></font>", ParagraphStyle('H2', alignment=1)),
        Spacer(1, 0.4*cm),
        Paragraph("<b>RELATÓRIO ESTATÍSTICO E CONSOLIDADO DE TODAS AS CONGREGAÇÕES</b>", ParagraphStyle('H3', alignment=1)),
        Spacer(1, 0.5*cm)
    ]
    
    t = Table(dados_tabela, colWidths=[4.2*cm, 3.8*cm, 2.0*cm, 2.8*cm, 2.8*cm, 2.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elementos.append(t)
    
    elementos.append(Spacer(1, 1.2*cm))
    elementos.append(Paragraph("____________________________________________<br/><b>Secretaria Geral e Superintendência Nacional</b>", ParagraphStyle('Ass', alignment=1, fontSize=9)))
    
    doc.build(elementos)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="Relatorio_Consolidado_SIGAD.pdf", mimetype='application/pdf')
"""

if 'def superadmin_estatisticas' not in codigo:
    codigo += rotas_estatisticas
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Rotas de estatísticas consolidadas e PDF integradas com sucesso no app.py!")
else:
    print("! As rotas de estatísticas já existem no app.py.")