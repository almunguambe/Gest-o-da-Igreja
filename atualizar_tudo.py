import os

with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Rotinas de PDF e Módulos do Manual Semestral
bloco_novas_rotas = '''
# ==============================================================================
# MANUAL DE DOUTRINA DE 6 MESES (24 LIÇÕES DETALHADAS)
# ==============================================================================
MODULOS_DOUTRINA_SEMESTRAL = [
    {
        "modulo": 1,
        "titulo": "Mês 1 – Fundamentos da Fé, Queda e Redenção",
        "licoes": [
            {"semana": 1, "tema": "A Criação de Deus e a Queda do Homem", "texto": "Gênesis 1 a 3. Compreensão do propósito divino, a desobediência original, a corrupção da natureza humana e a separação espiritual."},
            {"semana": 2, "tema": "O Plano Eterno da Redenção", "texto": "João 3:16; Isaías 53. A provisão vicária de Deus por meio da encarnação, vida imaculada e sacrifício expiatório de Cristo na cruz."},
            {"semana": 3, "tema": "Arrependimento e Confissão Bíblica", "texto": "Atos 3:19; 1 João 1:9. O reconhecimento sincero do pecado, a tristeza segundo Deus e a mudança radical de mente e direção moral."},
            {"semana": 4, "tema": "Justificação e Regeneração (O Novo Nascimento)", "texto": "Romanos 5:1; Tito 3:5. A reconciliação legal perante a justiça divina e a nova vida gerada pelo Espírito Santo."}
        ]
    },
    {
        "modulo": 2,
        "titulo": "Mês 2 – As Sagradas Escrituras e a Trindade Divina",
        "licoes": [
            {"semana": 5, "tema": "A Bíblia Sagrada: Inspiração e Inerrância", "texto": "2 Timóteo 3:16-17; 2 Pedro 1:20-21. Como a Palavra de Deus foi inspirada, a sua autoridade suprema e a regra inegociável de fé e conduta."},
            {"semana": 6, "tema": "Deus Pai: Soberania, Santidade e Amor", "texto": "Salmo 139; 1 João 4:8. A transcendência de Deus, Sua criação, sustento de todas as coisas e paternidade para com os salvos."},
            {"semana": 7, "tema": "Deus Filho: Divindade, Humanidade e Ministério", "texto": "João 1:1-14; Filipenses 2:5-11. A divindade eterna de Jesus Cristo, Sua ressurreição corpórea e intercessão à destra do Pai."},
            {"semana": 8, "tema": "Deus Espírito Santo: Pessoa, Papel e Convencimento", "texto": "João 16:7-14. O Consolador como terceira Pessoa da Trindade, que regenera, habita, guia e instrui o crente."}
        ]
    },
    {
        "modulo": 3,
        "titulo": "Mês 3 – As Ordenanças da Igreja e a Vida em Comunhão",
        "licoes": [
            {"semana": 9, "tema": "O Batismo nas Águas por Imersão", "texto": "Mateus 28:19; Romanos 6:3-4. O mandamento de Jesus: simbolismo da sepultura do velho homem e ressurreição para uma vida em novidade."},
            {"semana": 10, "tema": "Requisitos Bíblicos para o Batismo", "texto": "Marcos 16:16; Atos 8:36-38. Fé genuína, frutos visíveis de arrependimento e a declaração pública de lealdade a Cristo."},
            {"semana": 11, "tema": "A Santa Ceia do Senhor: Memória e Proclamação", "texto": "1 Coríntios 11:23-30. O pão e o fruto da vide como corpo e sangue de Cristo; autoexame, discernimento e comunhão santa."},
            {"semana": 12, "tema": "A Igreja como Corpo de Cristo e Família de Deus", "texto": "1 Coríntios 12:12-27; Efésios 4:1-6. Membros uns dos outros, submissão mútua, discipulado e compromisso na congregação local."}
        ]
    },
    {
        "modulo": 4,
        "titulo": "Mês 4 – Santificação, Oração e Mordomia Cristã",
        "licoes": [
            {"semana": 13, "tema": "Santificação Diária e Separação do Mundo", "texto": "1 Tessalonicenses 4:3-7; Hebreus 12:14. O processo contínuo de consagração e vitória sobre as concupiscências carnais."},
            {"semana": 14, "tema": "A Vida Devocional: Oração Eficaz e Jejum", "texto": "Mateus 6:5-18; Tiago 5:16. Prática sistemática de oração, adoração particular e busca de intimidade com Deus."},
            {"semana": 15, "tema": "Mordomia Financeira: Dízimos e Ofertas", "texto": "Malaquias 3:10; 2 Coríntios 9:6-8. Fidelidade nos dízimos como princípio de gratidão e sustentação da obra missionária e eclesial."},
            {"semana": 16, "tema": "A Conduta do Cristão na Família e na Sociedade", "texto": "Efésios 5:21-6:4; Mateus 5:13-16. Sal da terra e luz do mundo, pureza moral, casamentos santos e honra no trabalho."}
        ]
    },
    {
        "modulo": 5,
        "titulo": "Mês 5 – Doutrina Pentecostal e Poder do Espírito Santo",
        "licoes": [
            {"semana": 17, "tema": "A Promessa do Batismo no Espírito Santo", "texto": "Joel 2:28-29; Atos 1:8. Revestimento de poder concedido aos salvos para testemunhar o Evangelho com intrepidez."},
            {"semana": 18, "tema": "A Evidência Bíblica e as Línguas Estranhas", "texto": "Atos 2:1-4; 10:44-46. O dom de falar noutras línguas como confirmação bíblica inicial do batismo pentecostal."},
            {"semana": 19, "tema": "Os Dons Espirituais e a Edificação Coletiva", "texto": "1 Coríntios 12 e 14. Dons de revelação, poder e elocução: operação ordenada e orientada pelo amor cristão."},
            {"semana": 20, "tema": "Batalha Espiritual e a Armadura Completa de Deus", "texto": "Efésios 6:10-18. Resistência firme contra as ciladas das trevas, vigilância e triunfo em nome de Jesus."}
        ]
    },
    {
        "modulo": 6,
        "titulo": "Mês 6 – Grande Comissão, Ordem Eclesial e Esperança Bendita",
        "licoes": [
            {"semana": 21, "tema": "A Grande Comissão e Evangelismo Pessoal", "texto": "Marcos 16:15; Atos 4:20. O dever intransferível de cada crente de partilhar a mensagem do Evangelho no seu círculo social."},
            {"semana": 22, "tema": "Estrutura e Disciplina Eclesiástica da IEAD", "texto": "Hebreus 13:17; 1 Timóteo 3. Respeito à liderança pastoral, presbitério, diáconos e normas de convivência assembleiana."},
            {"semana": 23, "tema": "Escatologia Bíblica: O Arrebatamento e a Segunda Vinda", "texto": "1 Tessalonicenses 4:13-18; Tito 2:13. A bendita esperança da Igreja, julgamento vindouro e eternidade com Cristo."},
            {"semana": 24, "tema": "Exame Final de Fé e Preparação Prática para o Batismo", "texto": "Confissão pública dos artigos de fé, orientações práticas de vestimenta e consagração solene para as águas."}
        ]
    }
]

# ==============================================================================
# ROTAS PARA CERTIFICADO DE BATISMO, CARTA DE RECOMENDAÇÃO E CARTÃO
# ==============================================================================
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def obter_caminho_logo():
    caminhos = [
        os.path.join(app.root_path, 'static', 'img', 'logo.png'),
        os.path.join(app.root_path, 'static', 'logo.png'),
        os.path.join(app.root_path, 'logo.png')
    ]
    for c in caminhos:
        if os.path.exists(c):
            return c
    return None

@app.route('/membro/<int:id>/certificado_batismo')
def emitir_certificado_batismo(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
    membro = c.fetchone()
    conn.close()

    if not membro:
        return "Membro não encontrado", 404

    # Registro pode ser dict ou tuple
    nome = membro.get('nome') if isinstance(membro, dict) else membro[1]
    data_bat = membro.get('data_batismo') if isinstance(membro, dict) else (membro[5] if len(membro) > 5 else "____/____/________")
    if not data_bat:
        data_bat = "____/____/________"

    buffer = BytesIO()
    # Certificado em Paisagem A4
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elementos = []
    estilos = getSampleStyleSheet()

    logo_path = obter_caminho_logo()
    if logo_path:
        elementos.append(RLImage(logo_path, width=55, height=55))
        elementos.append(Spacer(1, 4))

    estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'))
    estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, alignment=1, textColor=colors.HexColor('#333333'))
    estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=26, alignment=1, textColor=colors.HexColor('#b38600'))
    estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=14, leading=22, alignment=1, textColor=colors.HexColor('#222222'))
    estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=20, alignment=1, textColor=colors.HexColor('#0d3b66'))

    elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
    elementos.append(Paragraph("MINISTÉRIO DE CHICUQUE – MOÇAMBIQUE", estilo_sub))
    elementos.append(Spacer(1, 15))
    elementos.append(Paragraph("CERTIFICADO DE BATISMO NAS ÁGUAS", estilo_tit))
    elementos.append(Spacer(1, 15))

    texto_cert = f"Certificamos que o(a) irmão(ã) abaixo mencionado(a), mediante confissão pública de fé no Senhor Jesus Cristo, desceu às águas batismais conforme a ordenança bíblica de Mateus 28:19:"
    elementos.append(Paragraph(texto_cert, estilo_corpo))
    elementos.append(Spacer(1, 15))
    elementos.append(Paragraph(f"<b>{nome.upper()}</b>", estilo_nome))
    elementos.append(Spacer(1, 15))
    elementos.append(Paragraph(f"Batizado(a) solenemente em nome do Pai, do Filho e do Espírito Santo.<br/>Data do Batismo: <b>{data_bat}</b>", estilo_corpo))
    elementos.append(Spacer(1, 35))

    tabela_ass = Table([
        ["_______________________________________", "_______________________________________"],
        ["Pastor Presidente", "Secretário Geral"]
    ], colWidths=[12*cm, 12*cm])
    tabela_ass.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#444444'))
    ]))
    elementos.append(tabela_ass)

    doc.build(elementos)
    buffer.seek(0)
    from flask import send_file
    return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f'Certificado_Batismo_{id}.pdf')

@app.route('/membro/<int:id>/carta_recomendacao')
def emitir_carta_recomendacao(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
    membro = c.fetchone()
    conn.close()

    if not membro:
        return "Membro não encontrado", 404

    nome = membro.get('nome') if isinstance(membro, dict) else membro[1]
    cargo = membro.get('cargo') if isinstance(membro, dict) else (membro[2] if len(membro) > 2 else "Membro")
    congregacao = membro.get('congregacao') if isinstance(membro, dict) else "Chicuque Sede"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementos = []
    estilos = getSampleStyleSheet()

    logo_path = obter_caminho_logo()
    if logo_path:
        elementos.append(RLImage(logo_path, width=60, height=60))
        elementos.append(Spacer(1, 8))

    estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=13, alignment=1, textColor=colors.HexColor('#0d3b66'))
    estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#444444'))
    estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, textColor=colors.HexColor('#222222'))
    estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, leading=18, alignment=4)

    elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
    elementos.append(Paragraph("COMUNIDADE DE CHICUQUE – PROVÍNCIA DE INHAMBANE", estilo_sub))
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("CARTA PASTORAL DE RECOMENDAÇÃO", estilo_tit))
    elementos.append(Spacer(1, 25))

    texto = f"""Aos Amados Irmãos em Cristo da Igreja Co-Irmã:<br/><br/>
    Pela presente, temos a honra de recomendar à vossa comunhão e aos santos cuidados o(a) nosso(a) estimado(a) irmão(ã) <b>{nome}</b>, que nesta congregação desempenha o cargo de <b>{cargo}</b>.<br/><br/>
    Enquanto esteve connosco na congregação de <b>{congregacao}</b>, manteve um testemunho exemplar, irrepreensível e fiel aos princípios das Sagradas Escrituras e aos estatutos eclesiásticos da nossa denominação.<br/><br/>
    Pedimos, pois, que o(a) recebam no Senhor de forma digna e fraternal, prestando-lhe todo o apoio e assistência espiritual que se fizer necessária para a contínua edificação do Reino de Deus.<br/><br/>
    <i>"Portanto, recebei-vos uns aos outros, como também Cristo nos recebeu para glória de Deus." (Romanos 15:7)</i>
    """
    elementos.append(Paragraph(texto, estilo_corpo))
    elementos.append(Spacer(1, 40))
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f'Carta_Recomendacao_{id}.pdf')

@app.route('/membro/<int:id>/cartao_membro')
def emitir_cartao_membro(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM membros WHERE id = %s" if DATABASE_URL and psycopg2 else "SELECT * FROM membros WHERE id = ?", (id,))
    membro = c.fetchone()
    conn.close()

    if not membro:
        return "Membro não encontrado", 404

    nome = membro.get('nome') if isinstance(membro, dict) else membro[1]
    cargo = membro.get('cargo') if isinstance(membro, dict) else (membro[2] if len(membro) > 2 else "Membro")
    num_membro = membro.get('id') if isinstance(membro, dict) else membro[0]

    buffer = BytesIO()
    # Cartão formato ID padrão (85mm x 55mm)
    doc = SimpleDocTemplate(buffer, pagesize=(86*mm, 54*mm), leftMargin=3*mm, rightMargin=3*mm, topMargin=3*mm, bottomMargin=3*mm)
    elementos = []

    logo_path = obter_caminho_logo()
    img_tag = RLImage(logo_path, width=22, height=22) if logo_path else ""

    estilos = getSampleStyleSheet()
    est_cab = ParagraphStyle('Cab', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=6.5, textColor=colors.white, alignment=1)
    est_sub = ParagraphStyle('SubC', parent=estilos['Normal'], fontName='Helvetica', fontSize=5, textColor=colors.HexColor('#ffd700'), alignment=1)
    est_dado = ParagraphStyle('Dado', parent=estilos['Normal'], fontName='Helvetica', fontSize=6, leading=8)

    tabela_cab = Table([[img_tag, [Paragraph("ASSEMBLEIA DE DEUS", est_cab), Paragraph("IEAD CHICUQUE", est_sub)]]], colWidths=[8*mm, 70*mm])
    tabela_cab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0d3b66')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2)
    ]))
    elementos.append(tabela_cab)
    elementos.append(Spacer(1, 2*mm))

    conteudo_cartao = [
        [Paragraph(f"<b>Nº Registo:</b> {num_membro:04d}", est_dado)],
        [Paragraph(f"<b>Nome:</b> {nome}", est_dado)],
        [Paragraph(f"<b>Cargo:</b> {cargo}", est_dado)],
        [Paragraph("<b>Status:</b> MEMBRO EM COMUNHÃO", est_dado)]
    ]
    tabela_corpo = Table(conteudo_cartao, colWidths=[78*mm])
    tabela_corpo.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1)
    ]))
    elementos.append(tabela_corpo)

    doc.build(elementos)
    buffer.seek(0)
    from flask import send_file
    return send_file(buffer, mimetype='application/pdf', as_attachment=False, download_name=f'Cartao_Membro_{id}.pdf')

@app.route('/manual_doutrina_semestral')
def ver_manual_doutrina_semestral():
    from flask import render_template_string
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Manual de Doutrina Semestral - IEAD Chicuque</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card-modulo { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.07); margin-bottom: 25px; }
            .header-modulo { background-color: #0d3b66; color: white; border-radius: 10px 10px 0 0; padding: 12px 20px; font-weight: bold; }
            .semana-badge { background-color: #f1c40f; color: #333; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; }
        </style>
    </head>
    <body class="p-3 p-md-5">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="text-primary fw-bold">Manual de Doutrina e Discipulado Semestral</h2>
                    <p class="text-muted">Programa de 6 Meses para Catecúmenos e Novos Convertidos (24 Lições)</p>
                </div>
                <a href="/" class="btn btn-outline-secondary">← Voltar ao Painel</a>
            </div>

            {% for m in modulos %}
            <div class="card card-modulo">
                <div class="header-modulo d-flex justify-content-between">
                    <span>{{ m.titulo }}</span>
                    <span class="badge bg-light text-dark">Módulo {{ m.modulo }}</span>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        {% for l in m.licoes %}
                        <div class="list-group-item py-3">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1 fw-bold text-dark"><span class="semana-badge me-2">Semana {{ l.semana }}</span>{{ l.tema }}</h6>
                            </div>
                            <p class="mb-1 text-muted mt-2">{{ l.texto }}</p>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, modulos=MODULOS_DOUTRINA_SEMESTRAL)
'''

# Injetar o bloco de rotas antes de if __name__ == '__main__':
if "MODULOS_DOUTRINA_SEMESTRAL =" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", bloco_novas_rotas + "\nif __name__ ==")
    else:
        conteudo += "\n" + bloco_novas_rotas

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py atualizado com Certificado, Recomendação, Cartão e Doutrina Semestral!")