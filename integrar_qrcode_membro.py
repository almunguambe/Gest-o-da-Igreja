with open('app.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. Garantir import do qrcode no topo se necessário
if 'import qrcode' not in codigo:
    codigo = "import qrcode\n" + codigo

# 2. Inserir a rota pública de validação antes do cartao_membro_pdf
rota_validacao = """@app.route('/validar/membro/<int:id>')
def validar_membro_publico(id):
    conn = get_db()
    membro = conn.execute("SELECT * FROM membros WHERE id = ?", (id,)).fetchone()
    cong_nome = "IEAD - Congregação Local"
    if membro and 'igreja_id' in membro.keys() and membro['igreja_id']:
        ig = conn.execute("SELECT nome FROM igrejas WHERE id = ?", (membro['igreja_id'],)).fetchone()
        if ig:
            cong_nome = ig['nome']
    conn.close()
    return render_template('validar_membro.html', membro=membro, congregacao_nome=cong_nome)

"""

if 'def validar_membro_publico' not in codigo:
    idx_cartao = codigo.find("@app.route('/membro/cartao_pdf/<int:id>')")
    if idx_cartao != -1:
        codigo = codigo[:idx_cartao] + rota_validacao + codigo[idx_cartao:]
        print("✓ Rota pública /validar/membro/<id> adicionada!")

# 3. Adicionar o desenho do QR Code na função cartao_membro_pdf
trecho_busca = '    c.setFillColor(colors.HexColor("#f8fafc"))\n'
trecho_qrcode = """    # Geração e Inserção do QR Code de Validação Oficial SIGAD
    try:
        url_validacao = request.host_url.rstrip('/') + f"/validar/membro/{m['id']}"
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url_validacao)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        qr_buf = io.BytesIO()
        img_qr.save(qr_buf, format='PNG')
        qr_buf.seek(0)
        
        # Moldura e QR Code no canto inferior direito do cartão
        c.setFillColor(colors.white)
        c.roundRect(6.6*cm, 0.4*cm, 1.5*cm, 1.5*cm, 2, fill=1, stroke=0)
        c.drawImage(ImageReader(qr_buf), 6.65*cm, 0.45*cm, width=1.4*cm, height=1.4*cm)
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica-Bold", 4.5)
        c.drawCentredString(7.35*cm, 0.2*cm, "VERIFICAR QR")
    except Exception as eqr:
        print(f"Aviso QR code cartao: {eqr}")

    c.setFillColor(colors.HexColor("#f8fafc"))
"""

if 'VERIFICAR QR' not in codigo:
    if trecho_busca in codigo:
        codigo = codigo.replace(trecho_busca, trecho_qrcode, 1)
        print("✓ Desenho do QR Code integrado no Cartão de Membro!")
    else:
        print("! Ponto de inserção de cores não encontrado exato.")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(codigo)