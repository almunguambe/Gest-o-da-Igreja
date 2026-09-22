with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

nova_carta = '''@app.route('/membro/<int:id>/carta_recomendacao')
@app.route('/membro/certificado_pdf/<int:id>/recomendacao')
def emitir_carta_recomendacao(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado.", 404

        dados = extrair_dados_membro(membro)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        elementos = []
        estilos = getSampleStyleSheet()

        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=65, height=65))
                elementos.append(Spacer(1, 8))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'))
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, textColor=colors.HexColor('#222222'))
        estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, leading=19, alignment=4)

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph(f"CONGREGAÇÃO DE {dados['bairro'].upper()} – MOÇAMBIQUE", estilo_sub))
        elementos.append(Spacer(1, 20))
        elementos.append(Paragraph("CARTA PASTORAL DE RECOMENDAÇÃO", estilo_tit))
        elementos.append(Spacer(1, 25))

        nome_l = dados['nome'].replace("<", "").replace(">", "")
        cargo_l = dados['posicao'].replace("<", "").replace(">", "")
        cong_l = dados['bairro'].replace("<", "").replace(">", "")
        depto_l = dados['departamento'].replace("<", "").replace(">", "")

        elementos.append(Paragraph("Aos Amados Irmãos em Cristo da Igreja Co-Irmã:", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Pela presente, temos a honra de recomendar à vossa comunhão e aos santos cuidados o(a) estimado(a) irmão(ã) <b>{nome_l}</b>, que serve nesta comunidade eclesial na qualidade de <b>{cargo_l}</b> (Ministério/Departamento: <b>{depto_l}</b>).", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Enquanto esteve connosco na congregação de <b>{cong_l}</b>, manteve um testemunho exemplar, irrepreensível e fiel aos princípios das Sagradas Escrituras e aos estatutos eclesiásticos da nossa denominação.", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("Rogamos que o(a) recebam no Senhor com todo o apreço e hospitalidade cristã, prestando-lhe todo o apoio e acompanhamento espiritual na continuação da sua jornada de fé.", estilo_corpo))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>&quot;Portanto, recebei-vos uns aos outros, como também Cristo nos recebeu para glória de Deus.&quot; (Romanos 15:7)</i>", estilo_corpo))
        elementos.append(Spacer(1, 35))
        elementos.append(Paragraph(f"{cong_l}, Moçambique.", estilo_corpo))
        elementos.append(Spacer(1, 35))

        tabela_ass = Table([
            ["__________________________________________", "__________________________________________"],
            ["Pastor Presidente / Titular", "Secretaria da Igreja"]
        ], colWidths=[8.5*cm, 8.5*cm])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9)
        ]))
        elementos.append(tabela_ass)

        doc.build(elementos)
        buffer.seek(0)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Carta_Recomendacao_{id}.pdf")
    except Exception as e:
        return f"Erro ao processar carta: {e}", 500
'''

if "def emitir_carta_recomendacao(id):" in conteudo:
    partes = conteudo.split("def emitir_carta_recomendacao(id):")
    topo = partes[0].rstrip()
    while topo.endswith(("@app.route('/membro/<int:id>/carta_recomendacao')", "@app.route('/membro/certificado_pdf/<int:id>/recomendacao')")):
        topo = topo.rsplit("\n", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + nova_carta + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Carta de Recomendação alinhada com os campos reais da tabela!")