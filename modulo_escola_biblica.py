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
            {
                "id": 1,
                "pergunta": "Qual a definição de pecar apresentada no manual?",
                "opcoes": [
                    "Errar o alvo da vontade de Deus e transgredir a Sua santa lei moral.",
                    "Um mero esquecimento momentâneo sem qualquer culpa ou juízo espiritual."
                ],
                "correta": 0
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
                "pergunta": "O que é a Justificação pela Fé segundo Romanos 5:1?",
                "opcoes": [
                    "O ato gracioso em que Deus declara o pecador justo pelos méritos de Jesus Cristo.",
                    "A conquista da salvação através do pagamento de penitências e esforço próprio."
                ],
                "correta": 0
            },
            {
                "id": 4,
                "pergunta": "O que caracteriza o verdadeiro Arrependimento bíblico?",
                "opcoes": [
                    "Tristeza segundo Deus que gera abandono do pecado e transformação prática de vida.",
                    "Apenas sentir remorso momentâneo sem mudar as atitudes diárias."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "Quem opera soberanamente o Novo Nascimento no crente?",
                "opcoes": [
                    "O Espírito Santo, mediante a fé em Cristo Jesus e na Sua Palavra.",
                    "O próprio homem unicamente pelo poder do seu pensamento positivo."
                ],
                "correta": 0
            },
            {
                "id": 6,
                "pergunta": "Como o ser humano foi originalmente formado por Deus?",
                "opcoes": [
                    "À imagem e semelhança do Criador, para viver em comunhão santa com Ele.",
                    "Por mero acaso da natureza e sem qualquer propósito eterno."
                ],
                "correta": 0
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
        