import os
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

CURRICULO_CLASSES = {
        "c1": {
        "nome": "Classe I — Primeiros Passos & Fundamentos da Salvação",
        "duracao": "Semanas 1 a 6",
        "ordem": 1,
        "proxima": "c2",
        "licoes": [
            {
                "numero": 1,
                "titulo": "O Pecado e o Perdão",
                "versiculo": "Romanos 6:23; 1 João 3:4",
                "conteudo": "Pecar significa errar o alvo da vontade de Deus e transgredir a Sua santa lei moral (Ex 20:3-17; 1Jo 3:4). Desobedecer é a causa que se gera no coração; transgredir é a manifestação exterior visível. A situação do homem sem Deus envolve: Imoralidade (desfiguração da imagem divina - Rm 3:9-12), Inimizade com Deus (separação espiritual - Is 59:2) e Morte espiritual (Rm 6:23). O Perdão decorre da justificação e da expiação no Calvário, pois sem derramamento de sangue não há remissão (Hb 9:22)."
            },
            {
                "numero": 2,
                "titulo": "Salvação e Senhorio de Cristo",
                "versiculo": "2 Coríntios 5:17; Efésios 2:8-10",
                "conteudo": "A Salvação é alcançada exclusivamente pela graça soberana mediante a fé, nunca por mérito humano (Ef 2:8-10). Passos fundamentais: Ouvir a Palavra (Rm 10:17), Crer (Jo 3:16), Arrepender-se e Confessar (1Jo 1:9) e Receber a Cristo (Jo 1:12). Jesus Cristo não deseja apenas livrar da condenação; Ele exige o senhorio integral sobre a nossa mente, finanças e decisões práticas diárias (1Co 8:6)."
            },
            {
                "numero": 3,
                "titulo": "O Testemunho Cristão",
                "versiculo": "Atos 1:8; 1 Pedro 3:1",
                "conteudo": "A testemunha fiel fala com convicção daquilo que viu, ouviu e experimentou em Cristo. A mensagem do crente é mais compreendida e respeitada pelo seu bom procedimento diário e conduta santa do que por palavras soltas (1Pe 3:1; Gl 6:9)."
            },
            {
                "numero": 4,
                "titulo": "A Pessoa de Deus Triuno",
                "versiculo": "Mateus 28:19; Deuteronômio 6:4",
                "conteudo": "Deus é numericamente Uno em essência e subsiste eternamente em três Pessoas coeternas: Pai, Filho e Espírito Santo (Mt 28:19; Dt 6:4). Possui atributos divinos absolutos: Omnipotente, Omnisciente, Omnipresente, Santo e Eterno."
            },
            {
                "numero": "4.1",
                "titulo": "Deus Pai: Criador e Soberano Sustentador",
                "versiculo": "1 Coríntios 8:6; Salmos 139:1-10",
                "conteudo": "A primeira Pessoa da Trindade; Criador soberano de todas as coisas, Juiz de toda a Terra e Pai compassivo que sustenta o universo com justiça e adota os crentes redimidos por Cristo."
            },
            {
                "numero": "4.2",
                "titulo": "Deus Filho: Plena Divindade e Perfeita Humanidade",
                "versiculo": "Hebreus 4:15; 1 Timóteo 2:5",
                "conteudo": "Jesus Cristo é o Verbo encarnado: verdadeiro Deus e verdadeiro Homem sem pecado (Hb 4:15). Exerce o tríplice ministério eterno: Profeta (revela a verdade), Sacerdote (ofereceu a Si mesmo e intercede) e Rei (governa soberanamente)."
            },
            {
                "numero": "4.3",
                "titulo": "Deus Espírito Santo: Consolador e Santificador",
                "versiculo": "João 14:26; Romanos 8:26",
                "conteudo": "Pessoa divina detentora de intelecto, sentimentos e vontade. Atua ativamente consolando os santos, convencendo o mundo do pecado, regenerando o pecador no Novo Nascimento e intercedendo pela Igreja com gemidos inexprimíveis (Jo 14:26; Rm 8:26)."
            },
            {
                "numero": 5,
                "titulo": "A Bíblia Sagrada — Manual de Fé e Prática",
                "versiculo": "2 Timóteo 3:16-17; 2 Pedro 1:21",
                "conteudo": "Composta por 66 livros inspirados por Deus através de cerca de 40 autores num período histórico de 1600 anos (2Tm 3:16). O Antigo Testamento tem 39 livros (Pentateuco, Históricos, Poéticos, Profetas Maiores e Menores) e o Novo Testamento tem 27 livros (Evangelhos, Histórico, Epístolas Paulinas, Epístolas Gerais e Apocalipse)."
            }
        ],
        "questionario": [
            {
                "id": 1,
                "pergunta": "Qual a definição de pecar apresentada no manual?",
                "opcoes": [
                    "Um esquecimento momentâneo sem culpa.",
                    "Errar o alvo da vontade de Deus e transgredir a Sua lei moral."
                ],
                "correta": 1
            },
            {
                "id": 2,
                "pergunta": "Quantos livros compõem a Bíblia Sagrada (AT e NT)?",
                "opcoes": [
                    "66 livros (39 no Antigo Testamento e 27 no Novo Testamento).",
                    "73 livros divididos de forma igual."
                ],
                "correta": 0
            },
            {
                "id": 3,
                "pergunta": "Segundo Efésios 2:8-10, como é alcançada a salvação em Cristo?",
                "opcoes": [
                    "Por mérito próprio, boas ações acumuladas e compra de favores divinos.",
                    "Pela graça divina mediante a fé, sendo dom gratuito de Deus."
                ],
                "correta": 1
            },
            {
                "id": 4,
                "pergunta": "O que é exigido para que haja remissão e perdão de pecados segundo Hebreus 9:22?",
                "opcoes": [
                    "Derramamento de sangue vicário, consumado no sacrifício de Cristo na cruz.",
                    "Cumprimento de penitências físicas e isolamento do mundo."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "Como a mensagem cristã é mais compreendida pelo mundo exterior?",
                "opcoes": [
                    "Pelo bom procedimento diário e conduta santa do que por palavras soltas.",
                    "Por debates agressivos e imposição forçada de opiniões."
                ],
                "correta": 0
            },
            {
                "id": 6,
                "pergunta": "Qual é o tríplice ministério exercido por Jesus Cristo?",
                "opcoes": [
                    "Juiz humano, filósofo moral e historiador sagrado.",
                    "Profeta, Sacerdote e Rei."
                ],
                "correta": 1
            },
            {
                "id": 7,
                "pergunta": "Qual é a natureza e a obra do Espírito Santo ensinada nas Escrituras?",
                "opcoes": [
                    "Uma força fluida impessoal que só atua em eventos cerimoniais.",
                    "Uma Pessoa divina que convence do pecado, regenera, consola e intercede pelos santos."
                ],
                "correta": 1
            }
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
            {
                "id": 1,
                "pergunta": "Qual a correta definição da Santíssima Trindade?",
                "opcoes": [
                    "Um só Deus verdadeiro que subsiste em três Pessoas coeternas: Pai, Filho e Espírito Santo.",
                    "Três deuses diferentes que agem separadamente em épocas distintas."
                ],
                "correta": 0
            },
            {
                "id": 2,
                "pergunta": "Quem é Jesus Cristo segundo João 1:1 e 1:14?",
                "opcoes": [
                    "O Verbo eterno que é verdadeiro Deus e se fez verdadeiro Homem.",
                    "Apenas um grande mestre humano ou profeta sem natureza divina."
                ],
                "correta": 0
            },
            {
                "id": 3,
                "pergunta": "O Espírito Santo é uma Pessoa divina ou uma força impessoal?",
                "opcoes": [
                    "Uma Pessoa divina da Trindade, dotada de intelecto, sentimentos e vontade.",
                    "Uma energia elétrica ou força fluida impessoal da natureza."
                ],
                "correta": 0
            },
            {
                "id": 4,
                "pergunta": "Segundo 1 Timóteo 2:5, quem é o único Mediador entre Deus e os homens?",
                "opcoes": [
                    "Jesus Cristo, homem.",
                    "Os espíritos dos antepassados ou líderes humanos intercessores."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "O que significa a inerrância e inspiração divina da Bíblia Sagrada?",
                "opcoes": [
                    "Que as Escrituras foram inspiradas por Deus e são regra infalível de fé e conduta.",
                    "Que a Bíblia contém mitos antigos sujeitos à opinião de cada pessoa."
                ],
                "correta": 0
            }
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
            {"numero": 18, "titulo": "Mordomia Cristã: Dízimos e Ofertas Sistemáticas", "versiculo": "Malaquias 3:10; 2 Coríntios 9:6-7", "conteudo": "A fidelidade financeira como confissão de que Deus é o Dono de tudo; a sustentação transparente e digna do ministério e das missões com espírito generoso e alegre."}
        ],
        "questionario": [
            {
                "id": 1,
                "pergunta": "Qual é a forma bíblica correta do Batismo nas Águas?",
                "opcoes": [
                    "Por imersão total do corpo em nome do Pai, do Filho e do Espírito Santo.",
                    "Por aspersão de algumas gotas de água na testa sem confissão prévia de fé."
                ],
                "correta": 0
            },
            {
                "id": 2,
                "pergunta": "O que representam os elementos da Ceia do Senhor (pão e cálice)?",
                "opcoes": [
                    "O corpo e o sangue expiatório de Cristo, celebrados em memória e comunhão santa.",
                    "Uma refeição cerimonial comum sem reverência espiritual ou valor sagrado."
                ],
                "correta": 0
            },
            {
                "id": 3,
                "pergunta": "O que 1 Coríntios 11:28 exige do crente antes de participar da Santa Ceia?",
                "opcoes": [
                    "Que examine a si mesmo a sua própria conduta perante o Senhor.",
                    "Que pague taxas eclesiásticas especiais para ter direito à mesa."
                ],
                "correta": 0
            },
            {
                "id": 4,
                "pergunta": "Qual é o dever do salvo quanto à Santificação Prática?",
                "opcoes": [
                    "Viver em santidade de conduta, palavra e testemunho íntegro no lar e na sociedade.",
                    "Viver da mesma forma que os incrédulos, pois a salvação não requer compromisso moral."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "O que ensina a doutrina da Mordomia Cristã (Dízimos e Ofertas)?",
                "opcoes": [
                    "Apoiar fiel e alegremente a obra de Deus reconhecendo que o Senhor é o Dono de tudo.",
                    "Uma forma de negociar favores, compras e privilégios com Deus."
                ],
                "correta": 0
            }
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
            {
                "id": 1,
                "pergunta": "Qual é a promessa do Batismo no Espírito Santo descrita em Atos 1:8?",
                "opcoes": [
                    "Revestimento sobrenatural de poder para testemunhar ousadamente de Cristo.",
                    "Garantia de que o cristão nunca mais enfrentará lutas ou enfermidades terrestres."
                ],
                "correta": 0
            },
            {
                "id": 2,
                "pergunta": "Qual é a evidência bíblica inicial do Batismo no Espírito Santo (Atos 2:4)?",
                "opcoes": [
                    "O falar em outras línguas conforme o Espírito concede que se fale.",
                    "Ter sensações emocionais passageiras sem respaldo das Escrituras."
                ],
                "correta": 0
            },
            {
                "id": 3,
                "pergunta": "Para que propósito Deus concede os Dons Espirituais à Igreja (1 Co 12:7)?",
                "opcoes": [
                    "Para a edificação mútua do Corpo de Cristo e avanço do Evangelho.",
                    "Para exaltação e vaidade pessoal de quem os manifesta."
                ],
                "correta": 0
            },
            {
                "id": 4,
                "pergunta": "Qual é a principal arma de ataque descrita na Armadura de Deus (Ef 6:17)?",
                "opcoes": [
                    "A Espada do Espírito, que é a Palavra viva de Deus.",
                    "A filosofia humana e o debate agressivo."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "Qual é a Bendita Esperança que aguardamos conforme 1 Tessalonicenses 4:16-17?",
                "opcoes": [
                    "A volta triunfal de Cristo nos ares para arrebatar a Sua Igreja fiel.",
                    "A reencarnação sucessiva em outros corpos no mundo terreno."
                ],
                "correta": 0
            }
        ]
    }
}

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
    elementos.append(Paragraph("MINISTÉRIO DE CHICUQUE – DEPARTAMENTO DE ENSINO BÍBLICO", estilo_sub))
    elementos.append(Paragraph("CERTIFICADO DE CONCLUSÃO DE DISCIPULADO", estilo_tit))

    elementos.append(Paragraph("Certificamos solenemente perante a Igreja de Deus que o(a) irmão(ã)", estilo_intro))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph(f"<b>{str(membro['nome']).upper()}</b>", estilo_nome))

    texto_detalhe = "concluiu com fidelidade, dedicação e aproveitamento exemplar as <b>24 Lições do Currículo Semestral de Doutrina e Discipulado</b> (Classes I a IV), demonstrando aprovação nas avaliações teológicas fundamentadas na sã doutrina das Sagradas Escrituras."
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