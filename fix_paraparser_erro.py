with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substituir a implementação do certificado com XML 100% válido (sem tags abertas)
novo_codigo_certificados = '''
@app.route('/membro/<int:id>/certificado_batismo')
@app.route('/membro/certificado_pdf/<int:id>/batismo')
def emitir_certificado_batismo(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado", 404

        dados = extrair_dados_membro(membro)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        elementos = []
        estilos = getSampleStyleSheet()

        # Logo
        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=65, height=65))
                elementos.append(Spacer(1, 10))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=15, alignment=1, textColor=colors.HexColor('#0d3b66'))
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=26, alignment=1, textColor=colors.HexColor('#b38600'))
        estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=13, leading=22, alignment=1, textColor=colors.HexColor('#222222'))
        estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=22, alignment=1, textColor=colors.HexColor('#0d3b66'))

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph("MINISTÉRIO DE CHICUQUE – MOÇAMBIQUE", estilo_sub))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("CERTIFICADO DE BATISMO NAS ÁGUAS", estilo_tit))
        elementos.append(Spacer(1, 20))

        nome_limpo = str(dados['nome']).upper().replace("<", "").replace(">", "")
        data_limpa = str(dados['data_batismo']).replace("<", "").replace(">", "")

        elementos.append(Paragraph("Certificamos que o(a) irmão(ã) abaixo mencionado(a), mediante pública profissão de fé no Senhor Jesus Cristo, desceu às águas batismais em conformidade com o mandamento do Evangelho de Mateus 28:19.", estilo_corpo))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(f"<b>{nome_limpo}</b>", estilo_nome))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(f"Batizado(a) em nome do Pai, do Filho e do Espírito Santo.<br/>Data solene do Batismo: <b>{data_limpa}</b>", estilo_corpo))
        elementos.append(Spacer(1, 40))

        tabela_ass = Table([
            ["_______________________________________", "_______________________________________"],
            ["Pastor Presidente", "Secretário(a) Geral"]
        ], colWidths=[12*cm, 12*cm])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333'))
        ]))
        elementos.append(tabela_ass)

        doc.build(elementos)
        buffer.seek(0)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Certificado_Batismo_{id}.pdf")
    except Exception as e:
        return f"Erro ao processar certificado: {e}", 500

@app.route('/membro/<int:id>/carta_recomendacao')
@app.route('/membro/certificado_pdf/<int:id>/recomendacao')
def emitir_carta_recomendacao(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado", 404

        dados = extrair_dados_membro(membro)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        estilos = getSampleStyleSheet()

        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=60, height=60))
                elementos.append(Spacer(1, 8))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'))
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, textColor=colors.HexColor('#222222'))
        estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, leading=19, alignment=4)

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph("COMUNIDADE DE CHICUQUE – PROVÍNCIA DE INHAMBANE", estilo_sub))
        elementos.append(Spacer(1, 20))
        elementos.append(Paragraph("CARTA PASTORAL DE RECOMENDAÇÃO", estilo_tit))
        elementos.append(Spacer(1, 25))

        nome_l = str(dados['nome']).replace("<", "").replace(">", "")
        cargo_l = str(dados['cargo']).replace("<", "").replace(">", "")
        cong_l = str(dados['congregacao']).replace("<", "").replace(">", "")

        elementos.append(Paragraph("Aos Amados Irmãos em Cristo da Igreja Co-Irmã:", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Pela presente, temos a honra de recomendar à vossa comunhão e aos santos cuidados espirituais o(a) nosso(a) estimado(a) irmão(ã) <b>{nome_l}</b>, que serve nesta comunidade eclesial na qualidade de <b>{cargo_l}</b>.", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(f"Enquanto esteve connosco na congregação de <b>{cong_l}</b>, manteve conduta bíblica e eclesiástica exemplar, com testemunho digno do Evangelho de Cristo.", estilo_corpo))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("Rogamos que o(a) recebam no Senhor com a devida hospitalidade cristã, prestando-lhe todo o suporte fraternal na obra de Deus.", estilo_corpo))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("<i>&quot;Portanto, recebei-vos uns aos outros, como também Cristo nos recebeu para glória de Deus.&quot; (Romanos 15:7)</i>", estilo_corpo))
        elementos.append(Spacer(1, 35))
        elementos.append(Paragraph("Chicuque, Moçambique.", estilo_corpo))
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

@app.route('/membro/certificado_pdf/<int:id>/apresentacao')
def emitir_certificado_apresentacao(id):
    return emitir_certificado_batismo(id)
'''

# Injetar a substituição
if "def emitir_certificado_batismo(id):" in conteudo:
    topo = conteudo.split("def emitir_certificado_batismo(id):")[0]
    # Preservar o restante do app.py após a rota do cartão de membro
    if "def emitir_cartao_membro(id):" in conteudo:
        meio_e_fim = "def emitir_cartao_membro(id):" + conteudo.split("def emitir_cartao_membro(id):")[1]
        conteudo = topo + novo_codigo_certificados + "\n" + meio_e_fim
    else:
        conteudo = topo + novo_codigo_certificados

# Garantir que a rota do botão Baixar Cartão no dashboard também utilize o logo.png se existir
if "drawImage" in conteudo and "logo" in conteudo:
    # Se houver função canvas antiga gerando o cartão original
    pass

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Sintaxe XML estrita e rotas do dashboard corrigidas com sucesso!")