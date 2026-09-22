with open("modulo_escola_biblica.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Questionários padronizados com 2 opções (A / B) para todas as classes
q_c1 = '''        "questionario": [
            {
                "id": 1,
                "pergunta": "Qual a definição bíblica de pecar apresentada no manual?",
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
                    "O ato gracioso em que Deus declara o pecador justo pelos méritos de Cristo.",
                    "A salvação conquistada pelo esforço próprio e cumprimento de rituais humanos."
                ],
                "correta": 0
            },
            {
                "id": 4,
                "pergunta": "O que caracteriza o verdadeiro Arrependimento bíblico?",
                "opcoes": [
                    "Tristeza segundo Deus que gera abandono do pecado e mudança de vida.",
                    "Sentir apenas remorso passageiro sem abandonar as más práticas."
                ],
                "correta": 0
            },
            {
                "id": 5,
                "pergunta": "Quem opera soberanamente o Novo Nascimento no coração do crente?",
                "opcoes": [
                    "O Espírito Santo, mediante a fé em Jesus e na Palavra de Deus.",
                    "O próprio homem unicamente através da sua força de vontade."
                ],
                "correta": 0
            },
            {
                "id": 6,
                "pergunta": "Como o ser humano foi originalmente formado por Deus em Gênesis?",
                "opcoes": [
                    "À imagem e semelhança do Criador, para comunhão santa com Ele.",
                    "Por um mero acaso da natureza e sem qualquer propósito eterno."
                ],
                "correta": 0
            }
        ]'''

q_c2 = '''        "questionario": [
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
        ]'''

q_c3 = '''        "questionario": [
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
        ]'''

q_c4 = '''        "questionario": [
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
        ]'''

# Inserção direta no dicionário do currículo
import re

# Substitui o bloco do questionário de cada classe
partes = conteudo.split('"c1": {')
inicio = partes[0] + '"c1": {'
resto_c1 = partes[1].split('"c2": {')

c1_corpo = resto_c1[0]
c1_corpo = re.sub(r'"questionario":\s*\[[\s\S]*?\]\s*\}', q_c1.strip() + '\n    }', c1_corpo)

resto_c2 = resto_c1[1].split('"c3": {')
c2_corpo = resto_c2[0]
c2_corpo = re.sub(r'"questionario":\s*\[[\s\S]*?\]\s*\}', q_c2.strip() + '\n    }', c2_corpo)

resto_c3 = resto_c2[1].split('"c4": {')
c3_corpo = resto_c3[0]
c3_corpo = re.sub(r'"questionario":\s*\[[\s\S]*?\]\s*\}', q_c3.strip() + '\n    }', c3_corpo)

c4_corpo = resto_c3[1]
c4_corpo = re.sub(r'"questionario":\s*\[[\s\S]*?\]\s*\}', q_c4.strip() + '\n    }', c4_corpo, count=1)

conteudo_final = inicio + c1_corpo + ',\n    "c2": {' + c2_corpo + ',\n    "c3": {' + c3_corpo + ',\n    "c4": {' + c4_corpo

with open("modulo_escola_biblica.py", "w", encoding="utf-8") as f:
    f.write(conteudo_final)

print("✓ Todos os questionários das Classes I, II, III e IV padronizados para o modelo A / B!")