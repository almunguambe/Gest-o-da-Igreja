with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

bloco_auxiliares = '''
def extrair_dados_membro(membro):
    """Extrai dados de forma segura quer venham de dicionário, sqlite3.Row ou tupla."""
    if isinstance(membro, dict):
        nome = membro.get('nome') or "Membro Sem Nome"
        cargo = membro.get('cargo') or "Membro"
        congregacao = membro.get('congregacao') or "Chicuque Sede"
        data_bat = membro.get('data_batismo')
        m_id = membro.get('id') or 1
    else:
        try:
            nome = membro['nome']
            cargo = membro['cargo']
            congregacao = membro['congregacao']
            data_bat = membro['data_batismo'] if 'data_batismo' in membro.keys() else None
            m_id = membro['id']
        except Exception:
            nome = membro[1] if len(membro) > 1 else "Membro Sem Nome"
            cargo = membro[2] if len(membro) > 2 else "Membro"
            congregacao = "Chicuque Sede"
            data_bat = membro[5] if len(membro) > 5 else None
            m_id = membro[0] if len(membro) > 0 else 1

    try:
        m_id = int(m_id)
    except:
        m_id = 1

    return {
        "id": m_id,
        "nome": str(nome).strip(),
        "cargo": str(cargo).strip(),
        "congregacao": str(congregacao).strip(),
        "data_batismo": str(data_bat).strip() if data_bat else None
    }
'''

bloco_rota_batismo_validada = '''
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
            return "Membro não encontrado.", 404

        dados = extrair_dados_membro(membro)

        # Condição obrigatória: deve ter data de batismo cadastrada
        if not dados['data_batismo'] or dados['data_batismo'].lower() in ['none', 'null', '', '____/____/________']:
            return """
            <div style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h3 style="color: #c0392b;">Certificado Indisponível</h3>
                <p>Este membro ainda não possui a <b>Data de Batismo</b> preenchida no seu cadastro.</p>
                <p>Por favor, edite a ficha do membro e informe a data em que foi batizado antes de emitir o certificado.</p>
                <a href="/" style="display: inline-block; margin-top: 15px; padding: 10px 20px; background-color: #0d3b66; color: white; text-decoration: none; border-radius: 5px;">Voltar ao Painel</a>
            </div>
            """, 400

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

        nome_limpo = dados['nome'].upper().replace("<", "").replace(">", "")
        data_limpa = dados['data_batismo'].replace("<", "").replace(">", "")

        elementos.append(Paragraph("Certificamos que o(a) irmão(ã) abaixo mencionado(a), mediante pública profissão de fé no Senhor Jesus Cristo, desceu às águas batismais em conformidade com o mandamento do Evangelho de Mateus 28:19.", estilo_corpo))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(f"<b>{nome_limpo}</b>", estilo_nome))
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(f"Batizado(a) solenemente em nome do Pai, do Filho e do Espírito Santo.<br/>Data do Batismo: <b>{data_limpa}</b>", estilo_corpo))
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
'''

# 1. Garantir que extrair_dados_membro exista antes das rotas
if "def extrair_dados_membro(" in conteudo:
    # Se já existir, remove a versão antiga para evitar duplicata
    partes = conteudo.split("def extrair_dados_membro(")
    conteudo = partes[0] + partes[1].split("\n@app.", 1)[-1]
    conteudo = "@app." + conteudo

# Inserir extrair_dados_membro logo após get_db_connection
if "def get_db_connection():" in conteudo:
    partes = conteudo.split("def get_db_connection():")
    topo = partes[0]
    corpo_resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "def get_db_connection():" + corpo_resto[0] + "\n" + bloco_auxiliares + "\n@app." + corpo_resto[1]

# 2. Substituir a rota emitir_certificado_batismo pela versão com a checagem da data
if "def emitir_certificado_batismo(id):" in conteudo:
    partes = conteudo.split("def emitir_certificado_batismo(id):")
    topo = partes[0].rstrip()
    # Remove as anotações @app.route que antecedem
    while topo.endswith(("@app.route('/membro/<int:id>/certificado_batismo')", "@app.route('/membro/certificado_pdf/<int:id>/batismo')")):
        topo = topo.rsplit("\n", 1)[0].rstrip()

    resto = partes[1].split("\n@app.", 1)
    conteudo = topo + "\n" + bloco_rota_batismo_validada + "\n@app." + resto[1]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Validação de Data de Batismo e função extrair_dados_membro aplicadas com sucesso!")