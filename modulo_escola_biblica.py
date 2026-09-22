import os
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ESTRUTURA COMPLETA DAS 4 CLASSES (24 LIÇÕES INDIVIDUAIS DE 6 MESES)
CURRICULO_CLASSES = {
    "c1": {
        "nome": "Classe I: Primeiros Passos & Fundamentos da Fé",
        "duracao": "Semanas 1 a 6",
        "ordem": 1,
        "proxima": "c2",
        "licoes": [
            {"numero": 1, "titulo": "A Criação de Deus e a Soberania Divina", "versiculo": "Gênesis 1:1; Salmos 24:1", "conteudo": "Estudo detalhado do propósito original da criação, a perfeição do universo criado por Deus e a dignidade outorgada ao ser humano como coroa da criação divina feita à imagem e semelhança do Criador."},
            {"numero": 2, "titulo": "A Queda do Homem e a Consequência do Pecado", "versiculo": "Gênesis 3:1-19; Romanos 3:23", "conteudo": "A entrada da desobediência no mundo através da serpente, a corrupção moral da humanidade, a morte física e a separação espiritual absoluta da presença santa de Deus."},
            {"numero": 3, "titulo": "O Plano Eterno da Redenção em Jesus Cristo", "versiculo": "Isaías 53:3-6; João 3:16", "conteudo": "A promessa messiânica da salvação, a encarnação do Verbo eterno, o sacrifício expiatório no Calvário e o perdão vicário consumado na cruz."},
            {"numero": 4, "titulo": "Arrependimento Bíblico e Mudança de Mente", "versiculo": "Atos 3:19; 2 Coríntios 7:10", "conteudo": "A distinção entre o remorso humano e o genuíno arrependimento espiritual perante Deus, implicando o abandono resoluto de práticas mundanas e a reorientação moral total."},
            {"numero": 5, "titulo": "A Justificação Exclusiva pela Fé", "versiculo": "Romanos 5:1; Gálatas 2:16", "conteudo": "Como o pecador culpado é declarado justo diante do tribunal divino pelos méritos da justiça de Cristo, excluindo qualquer presunção de salvação por obras meritórias humanas."},
            {"numero": 6, "titulo": "O Novo Nascimento e a Regeneração Espiritual", "versiculo": "João 3:3-7; Tito 3:5", "conteudo": "A transformação interior produzida de forma soberana pelo Espírito Santo na alma convertida, gerando uma nova criatura com novos afetos, valores e alvos eternos."}
        ],
        "questionario": [
            {"id": 1, "pergunta": "Qual foi a consequência imediata e espiritual da queda de Adão e Eva?", "opcoes": ["A perda da capacidade de pensar", "A separação espiritual de Deus e a entrada da morte", "A perda definitiva de qualquer redenção futura", "Nenhuma alteração significativa"], "correta": 1},
            {"id": 2, "pergunta": "Segundo Romanos 5:1, como somos justificados perante Deus?", "opcoes": ["Pelas nossas boas obras e esmolas", "Pela tradição dos antepassados", "Mediante a fé no sacrifício de Jesus Cristo", "Pela guarda estrita da lei mosaica"], "correta": 2},
            {"id": 3, "pergunta": "O que caracteriza o verdadeiro arrependimento conforme a Bíblia?", "opcoes": ["Apenas lamentar a dor da consequência", "Tristeza segundo Deus que opera mudança prática de vida e abandono do pecado", "Fazer penitências corporais", "Esquecer os erros sem confessá-los"], "correta": 1},
            {"id": 4, "pergunta": "Quem é o agente divino do Novo Nascimento?", "opcoes": ["O próprio homem pela sua força", "O Espírito Santo através da Palavra", "O pastor titular", "A liturgia eclesiástica"], "correta": 1},
            {"id": 5, "pergunta": "Segundo Efésios 2:8-9, a salvação é:", "opcoes": ["Dom gratuito de Deus, mediante a graça e pela fé", "Salário recebido pelo esforço próprio", "Conquistada pelo conhecimento filosófico", "Exclusiva para sacerdotes ordenados"], "correta": 0}
        ]
    },
    "c2": {
        "nome": "Classe II: As Sagradas Escrituras e a Trindade",
        "duracao": "Semanas 7 a 12",
        "ordem": 2,
        "proxima": "c3",
        "licoes": [
            {"numero": 7, "titulo": "A Inspiração Divina e Inerrância da Bíblia", "versiculo": "2 Timóteo 3:16-17; 2 Pedro 1:21", "conteudo": "Como os profetas e apóstolos foram inspirados pelo Espírito Santo, confirmando as Escrituras como regra infalível e suficiente de fé e prática para toda a vida."},
            {"numero": 8, "titulo": "Deus Pai: Soberano Criador e Juiz de Toda a Terra", "versiculo": "Salmo 139; Isaías 45:5-7", "conteudo": "Atributos incomunicáveis e comunicáveis de Deus: onisciência, onipresença, onipotência, justiça reta, santidade transcendente e amor leal paterno."},
            {"numero": 9, "titulo": "Deus Filho: Plena Divindade e Perfeita Humanidade", "versiculo": "João 1:1-14; Colossenses 2:9", "conteudo": "O ministério terreno de Jesus, Sua natureza teantrópica, milagres confirmadores, morte propiciatória e Sua ressurreição corpórea triunfante sobre a morte."},
            {"numero": 10, "titulo": "A Ascensão e Intercessão Celestial de Cristo", "versiculo": "Hebreus 7:25; Atos 1:9-11", "conteudo": "O ofício do Senhor Jesus como nosso Sumo Sacerdote à destra do Pai e o único Mediador legal e espiritual entre Deus e os homens."},
            {"numero": 11, "titulo": "Deus Espírito Santo: A Terceira Pessoa da Divindade", "versiculo": "João 14:16-26; 16:7-14", "conteudo": "O Consolador divino como Pessoa detentora de intelecto, vontade e sentimentos, incumbido de convencer o mundo do pecado, da justiça e do juízo vindouro."},
            {"numero": 12, "titulo": "A Doutrina Bíblica da Unidade na Trindade", "versiculo": "Mateus 28:19; 2 Coríntios 13:13", "conteudo": "A coexistência eterna de um só Deus vivo e verdadeiro em três Pessoas distintas, consubstanciais, coeternas e iguais em poder, glória e autoridade."}
        ],
        "questionario": [
            {"id": 1, "pergunta": "Quantas Pessoas subsistem na Trindade divina conforme as Escrituras?", "opcoes": ["Duas Pessoas", "Três Pessoas distintas em uma só essência divina", "Apenas uma que muda de forma", "Quatro manifestações celestiais"], "correta": 1},
            {"id": 2, "pergunta": "Qual é o único Mediador entre Deus e os seres humanos segundo 1 Timóteo 2:5?", "opcoes": ["Os anjos celestiais", "Os santos canonizados", "Jesus Cristo, homem", "A organização eclesiástica"], "correta": 2},
            {"id": 3, "pergunta": "O que significa dizer que as Escrituras são divinamente inspiradas?", "opcoes": ["Que homens piedosos escreveram por mera iluminação poética", "Que foram 'sopradas por Deus' pelo Espírito Santo guiando os autores bíblicos", "Que a Bíblia contém erros humanos aceitáveis", "Que cada leitor interpreta sem critério textual"], "correta": 1},
            {"id": 4, "pergunta": "Qual é uma das funções primordiais do Espírito Santo em relação ao incrédulo?", "opcoes": ["Garantir riqueza material imediata", "Convencê-lo do pecado, da justiça e do juízo", "Isolá-lo do convívio social", "Eliminar o livre-arbítrio"], "correta": 1},
            {"id": 5, "pergunta": "A ressurreição de Jesus Cristo ocorreu de que forma?", "opcoes": ["Apenas como uma ideia espiritual e mística", "Corpórea, glorificada e verificada por centenas de testemunhas", "Apenas em visões alegóricas dos discípulos", "Apenas temporária, tendo Ele falecido depois"], "correta": 1}
        ]
    },
    "c3": {
        "nome": "Classe III: Ordenanças da Igreja e Vida em Santidade",
        "duracao": "Semanas 13 a 18",
        "ordem": 3,
        "proxima": "c4",
        "licoes": [
            {"numero": 13, "titulo": "O Batismo nas Águas por Imersão Completa", "versiculo": "Mateus 28:19; Romanos 6:3-5", "conteudo": "A ordenança sagrada que simboliza publicamente a identificação do novo crente com a morte, sepultamento do velho homem e ressurreição para andar em novidade de vida."},
            {"numero": 14, "titulo": "A Ceia do Senhor: Memória, Comunhão e Proclamação", "versiculo": "1 Coríntios 11:23-32; Lucas 22:19-20", "conteudo": "A celebração contínua da redenção pelo pão e fruto da vide; o exame consciencioso da própria conduta para participar dignamente à mesa do Senhor."},
            {"numero": 15, "titulo": "A Santificação Prática e a Conduta Cristã", "versiculo": "1 Pedro 1:15-16; Hebreus 12:14", "conteudo": "O mandamento da separação da corrupção mundana; modéstia no vestir, integridade na linguagem, santidade moral no lar e honestidade nos negócios públicos."},
            {"numero": 16, "titulo": "A Vida Diária de Oração Fervorosa e Jejum", "versiculo": "Mateus 6:5-18; 1 Tessalonicenses 5:17", "conteudo": "A disciplina da oração constante como canal vital de comunhão, adoração e dependência exclusiva de Deus contra as tentações da carne."},
            {"numero": 17, "titulo": "A Família e o Casamento Segundo a Ordem Bíblica", "versiculo": "Efésios 5:22-33; Gênesis 2:24", "conteudo": "A instituição sagrada do matrimónio monogâmico e heterossexual; os papéis recíprocos de amor sacrificial, respeito mútuo e criação piedosa dos filhos no temor do Senhor."},
            {"numero": 18, "titulo": "Mordomia Cristã: Dízimos e Ofertas Sistemáticas", "versiculo": "Malaquias 3:10; 2 Coríntios 9:6-7", "conteudo": "A fidelidade financeira como confissão de que Deus é o Dono de tudo; a sustenção transparente e digna do ministério e das missões com espírito generoso e alegre."}
        ],
        "questionario": [
            {"id": 1, "pergunta": "Qual é a forma bíblica correta de administrar o Batismo nas Águas?", "opcoes": ["Por aspersão de algumas gotas na testa", "Por imersão total do corpo em nome do Pai, do Filho e do Espírito Santo", "Apenas por declaração verbal sem água", "Exclusivamente antes da confissão de fé"], "correta": 1},
            {"id": 2, "pergunta": "O que representam o pão e o cálice na Santa Ceia?", "opcoes": ["O corpo e o sangue expiatório de Cristo em memória memorial e comunhão", "Uma refeição social festiva e comum", "Um sacrifício repetido da cruz", "Apenas uma tradição humana sem reverência"], "correta": 0},
            {"id": 3, "pergunta": "O que as Escrituras advertem antes de participar da Ceia do Senhor em 1 Coríntios 11:28?", "opcoes": ["Pagar todas as dívidas financeiras", "Examine-se, pois, o homem a si mesmo", "Fazer jejum obrigatório de sete dias", "Pedir autorização aos parentes"], "correta": 1},
            {"id": 4, "pergunta": "O princípio bíblico da mordomia cristã ensina que:", "opcoes": ["O ser humano é dono absoluto dos seus recursos", "Deus é o Criador e Senhor de todas as coisas e nós somos mordomos fiéis", "O dinheiro é mau e deve ser desprezado", "Ofertar é uma compra de bênçãos divinas"], "correta": 1},
            {"id": 5, "pergunta": "Qual é o padrão bíblico de santificação requerido ao crente?", "opcoes": ["Apenas aparência externa religiosa", "Santidade integral: em corpo, alma e espírito, refletindo o caráter de Cristo", "Isolamento num mosteiro distante", "Cumprimento mecânico de costumes humanos"], "correta": 1}
        ]
    },
    "c4": {
        "nome": "Classe IV: Poder Pentecostal, Grande Comissão e Batismo",
        "duracao": "Semanas 19 a 24",
        "ordem": 4,
        "proxima": None,
        "licoes": [
            {"numero": 19, "titulo": "O Batismo no Espírito Santo e o Revestimento de Poder", "versiculo": "Atos 1:8; Joel 2:28-29", "conteudo": "A promessa divina para todos os crentes nascidos de novo: a capacitação sobrenatural para testemunhar o Evangelho com ousadia e eficácia ministerial."},
            {"numero": 20, "titulo": "O Falar em Línguas como Evidência Bíblica Inicial", "versiculo": "Atos 2:1-4; 10:44-46; 19:6", "conteudo": "A manifestação bíblica genuína registrada nos Atos dos Apóstolos que acompanha o batismo com o Espírito Santo na teologia assembleiana tradicional."},
            {"numero": 21, "titulo": "Os Dons Espirituais para a Edificação da Igreja", "versiculo": "1 Coríntios 12:4-11; 14:12", "conteudo": "A diversidade dos dons concedidos pelo Espírito: sabedoria, ciência, fé, curas, milagres, profecia, discernimento de espíritos, variedades de línguas e interpretação."},
            {"numero": 22, "titulo": "A Armadura de Deus e a Guerra Espiritual Triunfante", "versiculo": "Efésios 6:10-18; 2 Coríntios 10:4", "conteudo": "As táticas contra os ardis das trevas; a couraça da justiça, o escudo da fé, o capacete da salvação e a espada do Espírito, que é a Palavra de Deus."},
            {"numero": 23, "titulo": "A Grande Comissão e a Responsabilidade Missionária", "versiculo": "Marcos 16:15-18; Mateus 28:18-20", "conteudo": "O imperativo missionário de anunciar as Boas-Novas a todo o ser humano em Moçambique e até aos confins da Terra com compaixão e fidelidade bíblica."},
            {"numero": 24, "titulo": "A Esperança Escatológica: O Arrebatamento e a Glória", "versiculo": "1 Tessalonicenses 4:13-18; Tito 2:13", "conteudo": "A bendita esperança do retorno iminente de Cristo para arrebatar a Sua Noiva fiel, o Tribunal de Cristo, as Bodas do Cordeiro e o Reino Eterno de Deus."}
        ],
        "questionario": [
            {"id": 1, "pergunta": "Qual foi a promessa principal feita por Jesus em Atos 1:8?", "opcoes": ["Prosperidade material e fama terrena", "Recebereis poder, ao descer sobre vós o Espírito Santo, e sereis minhas testemunhas", "Ausência total de dificuldades mundanas", "Conhecimento de todas as ciências humanas"], "correta": 1},
            {"id": 2, "pergunta": "Qual é a evidência bíblica inicial do Batismo no Espírito Santo segundo a doutrina pentecostal?", "opcoes": ["Sentir calafrios emocionais", "O falar em outras línguas conforme o Espírito concede que se fale", "Cair desmaiado no templo", "Apenas cantar hinos sacros"], "correta": 1},
            {"id": 3, "pergunta": "Para que finalidade principal foram concedidos os Dons Espirituais (1 Co 12:7)?", "opcoes": ["Para exibição pessoal e vaidade", "Para a mútua e santa edificação do Corpo de Cristo", "Para estabelecer hierarquias sociais na igreja", "Apenas para líderes ordenados"], "correta": 1},
            {"id": 4, "pergunta": "Qual é a Espada do Espírito descrita na armadura de Efésios 6?", "opcoes": ["A retórica humana persuasiva", "A Palavra de Deus", "A disciplina física rígida", "A força da tradição religiosa"], "correta": 1},
            {"id": 5, "pergunta": "Qual é a Bendita Esperança descrita para os fiéis em 1 Tessalonicenses 4?", "opcoes": ["O estabelecimento de impérios terrenos passageiros", "O Arrebatamento da Igreja para o encontro com o Senhor nos ares", "A reencarnação noutros corpos terrestres", "O fim da existência da alma"], "correta": 1}
        ]
    }
}

# ==============================================================================
# CERTIFICADO MODERNO DE CONCLUSÃO DO DISCIPULADO BÍBLICO (A4 GALA)
# ==============================================================================
def gerar_pdf_conclusao_discipulado(membro, obter_caminho_logo_fn):
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

    logo_path = obter_caminho_logo_fn()
    if logo_path and os.path.exists(logo_path):
        try:
            elementos.append(RLImage(logo_path, width=70, height=70))
            elementos.append(Spacer(1, 4))
        except Exception:
            pass

    estilo_inst = ParagraphStyle('Inst', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=2)
    estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor('#555555'), spaceAfter=8)
    estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=23, alignment=1, textColor=colors.HexColor('#b38600'), spaceAfter=14)
    estilo_intro = ParagraphStyle('Intro', parent=estilos['Normal'], fontName='Helvetica', fontSize=11.5, leading=17, alignment=1, textColor=colors.HexColor('#444444'))
    estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=21, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=8)
    estilo_detalhes = ParagraphStyle('Detalhes', parent=estilos['Normal'], fontName='Helvetica', fontSize=11.5, leading=17, alignment=1, textColor=colors.HexColor('#222222'))
    estilo_versiculo = ParagraphStyle('Verso', parent=estilos['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=13, alignment=1, textColor=colors.HexColor('#666666'))

    elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
    elementos.append(Paragraph(f"MINISTÉRIO DE CHICUQUE – DEPARTAMENTO DE ENSINO BÍBLICO", estilo_sub))
    elementos.append(Paragraph("CERTIFICADO DE CONCLUSÃO DE DISCIPULADO", estilo_tit))

    elementos.append(Paragraph("Certificamos solenemente perante a Igreja de Deus que o(a) irmão(ã)", estilo_intro))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph(f"<b>{str(membro['nome']).upper()}</b>", estilo_nome))

    texto_detalhe = f"concluiu com fidelidade, dedicação e aproveitamento exemplar as <b>24 Lições do Currículo Semestral de Doutrina e Discipulado</b> (Classes I a IV), demonstrando aprovação nas avaliações teológicas fundamentadas na sã doutrina das Sagradas Escrituras."
    elementos.append(Paragraph(texto_detalhe, estilo_detalhes))
    elementos.append(Spacer(1, 10))

    versiculo = '&quot;Tu, porém, permanece naquilo que aprendeste, e de que foste inteirado, sabendo de quem o tens aprendido.&quot; — <b>2 Timóteo 3:14</b>'
    elementos.append(Paragraph(versiculo, estilo_versiculo))
    elementos.append(Spacer(1, 26))

    tabela_ass = Table([
        ["__________________________________________", "__________________________________________"],
        ["Pastor Presidente / Titular", "Diretor(a) da Escola Bíblica"]
    ], colWidths=[12.5*cm, 12.5*cm])
    tabela_ass.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('TOPPADDING', (0,0), (-1,-1), 4)
    ]))
    elementos.append(tabela_ass)

    def desenhar_moldura(canvas, d):
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
    return buffer