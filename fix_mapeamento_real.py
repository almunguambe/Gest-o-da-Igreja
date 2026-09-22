with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Nova função universal de extração com os nomes exatos das colunas da tabela membros
funcao_extracao_perfeita = '''def extrair_dados_membro(membro):
    """Extrai os dados de forma infalível usando o esquema real da base de dados."""
    def obter(chave, idx_padrao=None):
        if hasattr(membro, 'keys') and chave in membro.keys():
            return membro[chave]
        elif isinstance(membro, dict) and chave in membro:
            return membro[chave]
        elif idx_padrao is not None and not isinstance(membro, dict):
            try:
                return membro[idx_padrao]
            except:
                return None
        return None

    # Mapeamento estrito com base no PRAGMA table_info(membros)
    m_id = obter('id', 0) or 1
    nome = obter('nome', 1) or "Membro"
    telefone = str(obter('telefone', 2) or "").strip()
    faixa_etaria = obter('faixa_etaria', 5) or "Adulto"
    bairro = obter('bairro', 7) or "Chicuque Sede"
    tipo_doc = obter('tipo_documento', 9) or "BI"
    num_doc = obter('numero_documento', 10) or "---"
    ano_conv = obter('ano_conversao', 11) or "---"
    data_bat = obter('data_batismo', 12)
    posicao = obter('posicao_atual', 13) or "Membro em Comunhão"
    departamento = obter('departamento', 15) or "Geral"
    foto_path = obter('foto_path', 16) or ""

    # Formatar telefone moçambicano (+258 8x xxx xxxx)
    tel_limpo = "".join([c for c in telefone if c.isdigit()])
    if len(tel_limpo) == 9 and tel_limpo.startswith('8'):
        tel_fmt = f"(+258) {tel_limpo[:2]} {tel_limpo[2:5]} {tel_limpo[5:]}"
    elif len(tel_limpo) == 12 and tel_limpo.startswith('258'):
        tel_fmt = f"(+258) {tel_limpo[3:5]} {tel_limpo[5:8]} {tel_limpo[8:]}"
    else:
        tel_fmt = telefone if telefone else "Sem contacto"

    # Formatar data de batismo se válida
    data_bat_str = str(data_bat).strip() if data_bat else ""
    if data_bat_str.lower() in ['none', 'null', 'adulto', '']:
        data_bat_final = None
    else:
        partes = data_bat_str.split("-")
        if len(partes) == 3:
            data_bat_final = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            data_bat_final = data_bat_str

    return {
        "id": int(m_id) if str(m_id).isdigit() else 1,
        "nome": str(nome).strip(),
        "telefone": tel_fmt,
        "faixa_etaria": faixa_etaria,
        "bairro": str(bairro).strip(),
        "tipo_doc": str(tipo_doc).strip(),
        "num_doc": str(num_doc).strip(),
        "ano_conv": str(ano_conv).strip(),
        "data_batismo": data_bat_final,
        "posicao": str(posicao).strip(),
        "departamento": str(departamento).strip(),
        "foto_path": str(foto_path).strip()
    }
'''

# 1. Substituir a função extrair_dados_membro no app.py
if "def extrair_dados_membro(" in conteudo:
    partes = conteudo.split("def extrair_dados_membro(")
    topo = partes[0]
    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + funcao_extracao_perfeita + "\n@app." + resto[1]
else:
    # Injetar após get_db_connection
    if "def get_db_connection():" in conteudo:
        partes = conteudo.split("def get_db_connection():")
        corpo = partes[1].split("\n@app.", 1)
        conteudo = partes[0] + "def get_db_connection():" + corpo[0] + "\n" + funcao_extracao_perfeita + "\n@app." + corpo[1]

# 2. Corrigir o Certificado de Batismo para usar os dados validados
bloco_certificado_atualizado = '''@app.route('/membro/<int:id>/certificado_batismo')
@app.route('/membro/certificado_pdf/<int:id>/batismo')
def emitir_certificado_batismo(id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
        membro = c.fetchone()
        conn.close()

        if not membro:
            return "Membro não encontrado.", 404

        dados = extrair_dados_membro(membro)

        if not dados['data_batismo']:
            return """
            <div style="font-family: 'Segoe UI', Arial, sans-serif; text-align: center; margin-top: 60px; color: #333;">
                <div style="background: #fff; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #d9534f;">
                    <h3 style="color: #c9302c; margin-bottom: 10px;">Data de Batismo Necessária</h3>
                    <p style="color: #666; font-size: 15px; line-height: 1.5;">O membro selecionado ainda não tem a <b>Data de Batismo</b> registada na ficha.</p>
                    <p style="color: #888; font-size: 13px;">Preencha a data do batismo no formulário antes de gerar o documento solene.</p>
                    <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 24px; background-color: #0d3b66; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">Voltar ao Painel</a>
                </div>
            </div>
            """, 400

        buffer = BytesIO()
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
        elementos.append(Paragraph(f"CONGREGAÇÃO DE {dados['bairro'].upper()} – MOÇAMBIQUE", estilo_sub))
        elementos.append(Paragraph("CERTIFICADO DE BATISMO NAS ÁGUAS", estilo_tit))

        elementos.append(Paragraph("Certificamos para os devidos fins eclesiásticos que o(a) nosso(a) irmão(ã)", estilo_intro))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(f"<b>{dados['nome'].upper()}</b>", estilo_nome))

        texto_declaracao = f"tendo confessado publicamente a Jesus Cristo como seu Salvador pessoal, desceu às águas batismais por imersão em <b>{dados['data_batismo']}</b>, cumprindo a sagrada ordenança em nome do Pai, do Filho e do Espírito Santo."
        elementos.append(Paragraph(texto_declaracao, estilo_detalhes))
        elementos.append(Spacer(1, 10))

        versiculo = '&quot;Portanto ide, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo; ensinando-os a guardar todas as coisas que eu vos tenho mandado.&quot; — <b>Mateus 28:19-20</b>'
        elementos.append(Paragraph(versiculo, estilo_versiculo))
        elementos.append(Spacer(1, 28))

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

        def desenhar_moldura(canvas, doc):
            canvas.saveState()
            largura, altura = landscape(A4)
            canvas.setStrokeColor(colors.HexColor('#0d3b66'))
            canvas.setLineWidth(4)
            canvas.rect(1.2*cm, 1.2*cm, largura - 2.4*cm, altura - 2.4*cm)
            canvas.setStrokeColor(colors.HexColor('#d4af37'))
            canvas.setLineWidth(1.5)
            canvas.rect(1.5*cm, 1.5*cm, largura - 3.0*cm, altura - 3.0*cm)
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
    conteudo = topo + "\n" + bloco_certificado_atualizado + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Mapeamento perfeito das colunas e validações aplicadas!")