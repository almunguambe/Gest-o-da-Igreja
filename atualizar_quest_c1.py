with open("modulo_escola_biblica.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

novo_questionario_c1 = '''        "questionario": [
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
        ]'''

# Substitui o bloco do questionario da c1
if '"questionario": [' in conteudo:
    partes = conteudo.split('"questionario": [')
    cabecalho = partes[0]
    resto = partes[1].split('    },\n    "c2": {', 1)
    conteudo = cabecalho + novo_questionario_c1 + '\n    },\n    "c2": {' + resto[1]

with open("modulo_escola_biblica.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Questionário da Classe I atualizado para o formato direto A / B!")