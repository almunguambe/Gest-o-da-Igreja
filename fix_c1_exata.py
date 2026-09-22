with open("modulo_escola_biblica.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Bloco estrito da Classe I exatamente com as lições e as 2 questões enviadas
bloco_classe1 = '''    "c1": {
        "nome": "Classe I — Primeiros Passos & Fundamentos da Salvação",
        "duracao": "Semanas 1 a 6",
        "ordem": 1,
        "proxima": "c2",
        "licoes": [
            {
                "numero": 1,
                "titulo": "O Pecado e o Perdão",
                "versiculo": "Romanos 6:23",
                "conteudo": "Texto Áureo: \\"Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor.\\" (Rm 6:23)\\n\\nConceito: Pecar significa errar o alvo da vontade de Deus e transgredir a Sua lei moral (Ex 20:3-17; 1Jo 3:4). Desobedecer é a causa no coração; transgredir é a manifestação exterior visível.\\n\\nA Situação do Homem: Imoralidade (desfiguração da imagem divina - Rm 3:9-12), Inimizade com Deus (separação - Is 59:2) e Morte espiritual (Rm 6:23).\\n\\nO Perdão: Deus perdoou-nos em Cristo. Pela justificação e expiação, Cristo pagou as consequências do nosso pecado. Não há perdão sem derramamento de sangue (Hb 9:22)."
            },
            {
                "numero": 2,
                "titulo": "Salvação e Senhorio de Cristo",
                "versiculo": "2 Coríntios 5:17",
                "conteudo": "Texto Áureo: \\"Se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo.\\" (2Co 5:17)\\n\\nA Salvação é alcançada pela fé e graça, não por mérito humano (Ef 2:8-10). Passos fundamentais: Ouvir a Palavra (Rm 10:17), Crer (Jo 3:16), Arrepender-se e Confessar (1Jo 1:9) e Receber a Cristo (Jo 1:12). Ele não deseja apenas salvar; deseja reinar como Senhor e orientar as nossas decisões diárias (1Co 8:6)."
            },
            {
                "numero": 3,
                "titulo": "O Testemunho Cristão",
                "versiculo": "Atos 1:8",
                "conteudo": "Texto Áureo: \\"Mas recebereis a virtude do Espírito Santo, que há-de vir sobre vós; e ser-me-eis testemunhas...\\" (At 1:8)\\n\\nA testemunha fiel fala daquilo que viu, ouviu e experimentou em Cristo. A mensagem do crente é mais compreendida pelo seu bom procedimento diário do que por palavras soltas (1Pe 3:1; Gl 6:9)."
            },
            {
                "numero": 4,
                "titulo": "A Pessoa de Deus Triuno",
                "versiculo": "Mateus 28:19; Deuteronômio 6:4",
                "conteudo": "Deus é Uno e Triuno: subsiste no Pai, no Filho e no Espírito Santo (Mt 28:19; Dt 6:4). Possui atributos divinos: Omnipotente, Omnisciente, Omnipresente, Santo e Eterno."
            },
            {
                "numero": "4.1",
                "titulo": "Deus Pai: Criador Soberano",
                "versiculo": "1 Coríntios 8:6",
                "conteudo": "Deus Pai é a primeira Pessoa da Trindade, soberano Criador do céu e da terra e sustentador de todas as coisas."
            },
            {
                "numero": "4.2",
                "titulo": "Jesus Cristo: Plena Divindade e Humanidade",
                "versiculo": "Hebreus 4:15",
                "conteudo": "Jesus Cristo: Verdadeiro Deus e Homem perfeito (Hb 4:15). Ministério tríplice: Profeta, Sacerdote e Rei."
            },
            {
                "numero": "4.3",
                "titulo": "O Espírito Santo: Terceira Pessoa da Divindade",
                "versiculo": "João 14:26; Romanos 8:26",
                "conteudo": "O Espírito Santo: Pessoa divina que consola, convence do pecado, regenera o pecador e intercede pelos santos (Jo 14:26; Rm 8:26)."
            },
            {
                "numero": 5,
                "titulo": "A Bíblia Sagrada — Manual de Fé",
                "versiculo": "2 Timóteo 3:16",
                "conteudo": "Composta por 66 livros inspirados por Deus através de cerca de 40 autores num período de 1600 anos (2Tm 3:16). O Antigo Testamento tem 39 livros (Pentateuco, Históricos, Poéticos, Profetas Maiores e Menores) e o Novo Testamento tem 27 livros (Evangelhos, Histórico, Epístolas Paulinas, Epístolas Gerais e Revelação/Apocalipse)."
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
            }
        ]
    }'''

partes = conteudo.split('"c1": {')
inicio = partes[0]
resto = partes[1].split('    "c2": {', 1)

conteudo_final = inicio + bloco_classe1 + ',\n    "c2": {' + resto[1]

with open("modulo_escola_biblica.py", "w", encoding="utf-8") as f:
    f.write(conteudo_final)

print("✓ Classe I configurada exatamente com o texto do manual e as 2 questoes oficiais!")