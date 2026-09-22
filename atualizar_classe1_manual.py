with open("modulo_escola_biblica.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Bloco estrito da Classe I com os textos integrais e as 7 questoes A/B
c1_atualizada = '''    "c1": {
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
    }'''

partes = conteudo.split('"c1": {')
inicio = partes[0]
resto = partes[1].split('    "c2": {', 1)

conteudo_final = inicio + c1_atualizada + ',\n    "c2": {' + resto[1]

with open("modulo_escola_biblica.py", "w", encoding="utf-8") as f:
    f.write(conteudo_final)

print("✓ Conteúdo integral da Classe I e questionário A/B inseridos no módulo com sucesso!")