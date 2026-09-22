with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

novo_bloco_certificado = '''
@app.route('/membro/<int:id>/certificado_batismo')
@app.route('/membro/certificado_pdf/<int:id>/batismo')
def emitir_certificado_batismo(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        query = "SELECT id, nome, cargo, congregacao, data_batismo FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT id, nome, cargo, congregacao, data_batismo FROM membros WHERE id = ?"
        c.execute(query, (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado.", 404

        if isinstance(membro, dict):
            nome = membro.get('nome') or "MEMBRO"
            data_bat = membro.get('data_batismo')
            congregacao = membro.get('congregacao') or "Chicuque"
        else:
            nome = membro[1]
            data_bat = membro[4]
            congregacao = membro[3] or "Chicuque"

        data_bat_str = str(data_bat).strip() if data_bat else ""
        if not data_bat_str or data_bat_str.lower() in ['none', 'null', '', 'adulto']:
            return """
            <div style="font-family: 'Segoe UI', Arial, sans-serif; text-align: center; margin-top: 60px; color: #333;">
                <div style="background: #fff; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #d9534f;">
                    <h3 style="color: #c9302c; margin-bottom: 10px;">Data de Batismo Necessária</h3>
                    <p style="color: #666; font-size: 15px; line-height: 1.5;">O membro selecionado ainda não tem a <b>Data de Batismo</b> registada no cadastro.</p>
                    <p style="color: #888; font-size: 13px;">Abra a ficha do membro, informe a data em que desceu às águas e tente emitir novamente.</p>
                    <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 24px; background-color: #0d3b66; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">Voltar ao Painel</a>
                </div>
            </div>
            """, 400

        # Formatar data de YYYY-MM-DD para DD/MM/AAAA se aplicável
        partes_data = data_bat_str.split("-")
        if len(partes_data) == 3:
            data_formatada = f"{partes_data[2]}/{partes_data[1]}/{partes_data[0]}"
        else:
            data_formatada = data_bat_str

        buffer = BytesIO()
        # Margens estreitas para o canvas desenhar a moldura de gala
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=2.5*cm,
            rightMargin=2.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        elementos = []
        estilos = getSampleStyleSheet()

        # Logotipo Oficial no topo
        logo_path = obter_caminho_logo()
        if logo_path and os.path.exists(logo_path):
            try:
                elementos.append(RLImage(logo_path, width=70, height=70))
                elementos.append(Spacer(1, 4))
            except Exception:
                pass

        estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=2)
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#666666'), spaceAfter=10)
        estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=24, alignment=1, textColor=colors.HexColor('#b38600'), spaceAfter=14)
        estilo_intro = ParagraphStyle('Intro', parent=estilos['Normal'], fontName='Helvetica', fontSize=12, leading=18, alignment=1, textColor=colors.HexColor('#444444'))
        estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=22, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=8)
        estilo_detalhes = ParagraphStyle('Detalhes', parent=estilos['Normal'], fontName='Helvetica', fontSize=12, leading=18, alignment=1, textColor=colors.HexColor('#333333'))
        estilo_versiculo = ParagraphStyle('Verso', parent=estilos['Normal'], fontName='Helvetica-Oblique', fontSize=9.5, leading=14, alignment=1, textColor=colors.HexColor('#777777'))

        elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
        elementos.append(Paragraph(f"CONGREGAÇÃO DE {str(congregacao).upper()} – MOÇAMBIQUE", estilo_sub))
        elementos.append(Paragraph("CERTIFICADO DE BATISMO NAS ÁGUAS", estilo_tit))
        
        elementos.append(Paragraph("Certificamos para os devidos fins eclesiásticos que o(a) nosso(a) irmão(ã)", estilo_intro))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(f"<b>{str(nome).upper()}</b>", estilo_nome))
        
        texto_declaracao = f"tendo confessado publicamente a Jesus Cristo como seu único e suficiente Salvador pessoal, desceu às águas batismais por imersão em <b>{data_formatada}</b>, cumprindo solenemente a ordem do Senhor Jesus Cristo em nome do Pai, do Filho e do Espírito Santo."
        elementos.append(Paragraph(texto_declaracao, estilo_detalhes))
        elementos.append(Spacer(1, 10))

        versiculo = '&quot;Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo; ensinando-os a guardar todas as coisas que eu vos tenho mandado.&quot; — <b>Mateus 28:19-20</b>'
        elementos.append(Paragraph(versiculo, estilo_versiculo))
        elementos.append(Spacer(1, 28))

        # Tabela com as linhas de assinatura formal
        tabela_ass = Table([
            ["__________________________________________", "__________________________________________"],
            ["Pastor Presidente / Titular", "Secretaria Geral da Igreja"]
        ], colWidths=[12.5*cm, 12.5*cm])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#444444')),
            ('TOPPADDING', (0,0), (-1,-1), 4)
        ]))
        elementos.append(tabela_ass)

        # Função interna para desenhar a moldura moderna no fundo do certificado
        def desenhar_moldura(canvas, doc):
            canvas.saveState()
            largura, altura = landscape(A4)
            
            # Moldura externa azul marinho
            canvas.setStrokeColor(colors.HexColor('#0d3b66'))
            canvas.setLineWidth(4)
            canvas.rect(1.2*cm, 1.2*cm, largura - 2.4*cm, altura - 2.4*cm)
            
            # Moldura interna dourada clássica
            canvas.setStrokeColor(colors.HexColor('#d4af37'))
            canvas.setLineWidth(1.5)
            canvas.rect(1.5*cm, 1.5*cm, largura - 3.0*cm, altura - 3.0*cm)
            
            # Cantos decorativos nos 4 vértices
            canto = 0.6*cm
            canvas.setFillColor(colors.HexColor('#0d3b66'))
            canvas.rect(1.5*cm, altura - 1.5*cm - canto, canto, canto, fill=1, stroke=0)
            canvas.rect(largura - 1.5*cm - canto, altura - 1.5*cm - canto, canto, canto, fill=1, stroke=0)
            canvas.rect(1.5*cm, 1.5*cm, canto, canto, fill=1, stroke=0)
            canvas.rect(largura - 1.5*cm - canto, 1.5*cm, canto, canto, fill=1, stroke=0)
            
            canvas.restoreState()

        doc.build(elementos, onFirstPage=desenhar_moldura)
        buffer.seek(0)
        from flask import send_file
        return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f"Certificado_Batismo_{id}.pdf")
    except Exception as e:
        return f"Erro ao processar certificado: {e}", 500
'''

if "def emitir_certificado_batismo(id):" in conteudo:
    partes = conteudo.split("def emitir_certificado_batismo(id):")
    topo = partes[0].rstrip()
    while topo.endswith(("@app.route('/membro/<int:id>/certificado_batismo')", "@app.route('/membro/certificado_pdf/<int:id>/batismo')")):
        topo = topo.rsplit("\n", 1)[0].rstrip()
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + novo_bloco_certificado + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Certificado Moderno com bordas solenes e colunas SQL nominais aplicado!")