# -*- coding: utf-8 -*-
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

CURRICULO_CLASSES = {
    "c1": {
        "nome": "Classe I — Primeiros Passos",
        "duracao": "Semanas 1 a 6",
        "ordem": 1,
        "proxima": "c2",
        "licoes": [
            {
                "numero": "1",
                "titulo": "O Pecado e o Perdão",
                "versiculo": "Romanos 6:23",
                "conteudo": """<b>Texto Áureo:</b> <i>"Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor."</i> — Rm 6:23<br/><br/>
<b>I - O PECADO</b><br/>
1. Se o pecado não fosse uma triste realidade seria desnecessária a Salvação consumada por Jesus no Calvário. Pecar significa <b>Errar o Alvo</b>, errar o alvo de fazer a Vontade de Deus e assim ferimos a Sua santidade e seus propósitos para nossas vidas.<br/>
2. Pecar significa <b>Transgredir a Lei de Deus</b>; Uma pessoa que transgride a Lei Moral de Deus está em desobediência ao Criador (Êx 20:3-17; 1Jo 3:4; Rm 5:14,19; Rm 8:7). A diferença entre transgredir e desobedecer é: <i>Desobedecer é a causa e Transgredir o efeito</i>. A desobediência está escondida no coração e a transgressão sempre está exposta.<br/>
3. A SITUAÇÃO DO HOMEM PERANTE O PECADO:<br/>
• <b>Imoralidade:</b> Desfiguração da imagem divina (Rm 3:9-12).<br/>
• <b>Inimigo:</b> Separação da presença de Deus (Is 59:2; Gl 5:4).<br/>
• <b>Morte:</b> Separação definitiva do Criador (Rm 3:23; Rm 6:23a).<br/>
4. Posição do Homem para se libertar do pecado: Reconhecer que é pecador (Sl 51:3; Rm 3:23); Saber que Deus ama o pecador (Jo 3:16; Rm 5:8); Arrepender-se dos seus pecados (Sl 51:1; At 2:37,38); Crer e aceitar a Cristo como Salvador e Senhor (Jo 1:12; Jo 3:3,18; At 16:30,31; 1Jo 5:12,13).<br/><br/>
<b>II - O PERDÃO</b><br/>
1. Deus nos perdoou em Cristo (Mc 2:5; Lc 7:48; 1Jo 1:9). Expiou, pagou as consequências do nosso pecado, nos deu a propiciação, proporcionou, ou pagou com sua própria vida o preço justo da ira de Deus sobre o homem pecador.<br/>
2. Deus não se lembra mais dos nossos pecados (Is 43:25; Is 55:7; Mq 7:19).<br/>
3. Devemos perdoar-nos uns aos outros (Mt 18:33,35; Lc 17:4; Ef 4:32).<br/>
4. Não há perdão sem derramamento de sangue (Hb 9:22).<br/>
5. É importante vivermos perdoando para podermos ser perdoados (Mt 6:15). Quando Cristo perdoa, não só tira o pecado mas coloca o bem que o substitui."""
            },
            {
                "numero": "2",
                "titulo": "Salvação e Senhorio de Cristo",
                "versiculo": "2 Coríntios 5:17",
                "conteudo": """<b>Texto Áureo:</b> <i>"Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo."</i> — 2Co 5:17<br/><br/>
1. A separação entre Deus e os Homens é resultado do pecado (Rm 3:23; Is 59:2). Somos salvos por meio da fé e não por obras, sendo que estas deverão acompanhá-las como resultado da mesma (Ef 2:5,8,9,10). Estávamos longe, mas pelo Seu sangue chegamos perto (Ef 2:13).<br/>
2. A Bíblia nos dá a certeza da Salvação (Rm 10:8-10; Jo 5:24).<br/>
3. <b>PASSOS PARA NOS TORNARMOS FILHOS DE DEUS:</b><br/>
a) Ouvir Sua Palavra (Rm 10:17; Jo 5:24);<br/>
b) Crer no que a Sua Palavra diz (At 13:39; Jo 3:16-18);<br/>
c) Arrepender-se e Confessar nossos pecados (Rm 10:9; 1Jo 1:9; Lc 5:32; At 26:20);<br/>
d) Receber Cristo em nossa vida (Jo 1:12; Ap 3:20).<br/>
4. Ao milagre que acontece depois, chama-se de Novo Nascimento: Reconciliação com Deus (Cl 1:21,22), Filiação divina (Jo 3:1-8) e Vida Eterna (Jo 5:24).<br/>
5. <b>CRISTO QUER SER SALVADOR E SENHOR:</b> Cristo não só pode e quer Salvar, mas também deseja Dominar nossas vidas. Ele é o Senhor (Jo 13:13; At 10:36), e deve orientar nossas decisões diárias (1Co 8:6; 2Co 5:15)."""
            },
            {
                "numero": "3",
                "titulo": "O Testemunho",
                "versiculo": "Atos 1:8",
                "conteudo": """<b>Texto Áureo:</b> <i>"Mas recebereis a virtude do Espírito Santo, que há-de vir sobre vós; e ser-me-eis testemunhas, tanto em Jerusalém como em toda a Judeia e Samaria, e até aos confins da terra."</i> — At 1:8<br/><br/>
1. Um dos propósitos principais para o qual Deus nos salvou foi sermos Suas testemunhas (At 4:20; Is 43:10), e testemunhas incessantemente (Is 62:6).<br/>
2. É um dever diário de cada crente (Ml 3:16; Mt 9:31; Mc 16:15).<br/>
3. A verdadeira testemunha fala do que sabe (Jo 3:11), do que viu e ouviu (At 4:20), do que sente (Fp 2:2), do que crê (2Co 4:13) e do que vive (1Co 9:14).<br/>
4. <b>A mensagem da testemunha pode ser sábia e verdadeira, mas o mundo aprende melhor a lição observando o que ela faz</b> (Gl 6:9; Lc 6:31; 1Pe 3:1).<br/>
5. O Espírito Santo é quem fortalece a fiel testemunha (At 1:8)."""
            },
            {
                "numero": "4",
                "titulo": "A Pessoa de Deus Triuno",
                "versiculo": "Salmos 19:1; Deuteronómio 6:4",
                "conteudo": """<b>Texto Áureo:</b> <i>"Os céus manifestam a glória de Deus e o firmamento anuncia as obras de suas mãos."</i> — Sl 19:1<br/><br/>
1. <b>A Trindade Divina:</b> Deus é Uno e ao mesmo tempo Triuno, isto é, a unidade de Deus é uma unidade composta (Gn 1:1,26; Mt 3:16,17; Jo 14:16; Hb 9:14). Não existem três deuses, mas Um Só Deus operando em três Pessoas (Dt 6:4; 1Jo 5:7).<br/>
• Deus Pai: Plenitude da divindade Invisível.<br/>
• Deus Filho: Plenitude da divindade Manifesta.<br/>
• Deus Espírito Santo: Plenitude da divindade Operando na criatura.<br/>
2. <b>Atributos de Deus:</b> Deus é Espírito Infinito, Perfeito, Eterno e Imutável. É Omnipotente, Omnisciente e Omnipresente (Sl 139:1-12; Sl 90:2; Ml 3:6). Ele é Santidade, Rectidão, Justiça, Amor e Verdade (1Jo 4:8).<br/>
3. Natureza de Deus: Sua Auto-Existência ("Eu Sou o que Sou" - Êx 3:14) e Sua Espiritualidade (incorpóreo - Jo 4:24)."""
            },
            {
                "numero": "4.1",
                "titulo": "A Pessoa do Pai",
                "versiculo": "Mateus 5:48",
                "conteudo": """<b>Texto Áureo:</b> <i>"Sede vós, pois, perfeitos, como é o vosso Pai, que está nos céus."</i> — Mt 5:48<br/><br/>
I. <b>Atributos:</b> O Pai é Santo (Lv 11:45), o Pai ama profundamente (1Jo 3:1), a perfeição e a misericórdia são Suas qualidades essenciais (Mt 5:48; Lc 6:36).<br/>
II. <b>Adoração:</b> Deve ser adorado em espírito e em verdade (Jo 4:23); devemos orar em secreto ao Pai (Mt 6:6; Jo 17:1).<br/>
III. <b>Obras:</b> Jesus testificou d'Ele em obediência (Jo 14:31); Ele é o planeador soberano de todas as coisas (At 1:7); d'Ele procede o Espírito Santo (Jo 15:26); o Pai é o abençoador por excelência (Ef 1:3).<br/>
IV. <b>Relacionamento:</b> É a vontade do Pai que ninguém se perca (Jo 6:39); Ele guarda os Seus filhos fiéis no mundo (Jo 17:11)."""
            },
            {
                "numero": "4.2",
                "titulo": "A Pessoa de Jesus Cristo",
                "versiculo": "João 14:6",
                "conteudo": """<b>Texto Áureo:</b> <i>"Disse-lhe Jesus: Eu sou o caminho, e a verdade e a vida. Ninguém vem ao Pai, senão por mim."</i> — Jo 14:6<br/><br/>
1. <b>Divindade de Cristo:</b> Revelada amplamente na Bíblia (Jo 1:1-3; Jo 10:30; Cl 2:9; Hb 1:1-8). O nome Jesus significa 'O Senhor é Salvador' e Cristo/Messias significa 'O Ungido'.<br/>
2. <b>Humanidade Perfeita:</b> O Homem Perfeito sem pecado (Hb 4:15), o Filho Unigénito (Jo 3:16) e o Verbo Pré-existente (Jo 1:1; Jo 8:58).<br/>
3. <b>Propósito da Encarnação:</b> Revelar Deus aos homens (Jo 14:8-11), resgatar o homem da prisão do pecado pelo sacrifício da cruz (Hb 9:28) e preparar o homem para um destino eterno com Deus (Fp 3:21).<br/>
4. <b>Ministério Tríplice:</b> Profeta (Lc 7:16), Sacerdote (Hb 7:25) e Rei (Mt 2:2; Ap 22:5).<br/>
5. <b>Ressurreição Corpórea:</b> Prova final da Sua divindade. Todos os líderes de religiões morreram e os seus túmulos continuam ocupados; Cristo ressuscitou e vive para sempre!"""
            },
            {
                "numero": "4.3",
                "titulo": "A Pessoa do Espírito Santo",
                "versiculo": "João 14:26",
                "conteudo": """<b>Texto Áureo:</b> <i>"Mas aquele Consolador, o Espírito Santo, que o Pai enviará em meu nome, esse vos ensinará todas as coisas, e vos fará lembrar de tudo quanto vos tenho dito."</i> — Jo 14:26<br/><br/>
1. <b>Nomes Bíblicos:</b> Espírito de Deus (Rm 8:9), Consolador (Jo 14:16,26), Espírito de Cristo (Rm 8:9) e Espírito da Verdade (Jo 16:13).<br/>
2. <b>Divindade e Atributos:</b> Ele é Deus (At 5:3,4); possui Omnipresença (Sl 139:7-10), Omnisciência (1Co 2:10) e Omnipotência (Lc 1:35).<br/>
3. <b>Ministério Operacional:</b> Convencer o mundo do pecado, da justiça e do juízo (Jo 16:7,8); regenerar o homem no Novo Nascimento (Tt 3:5; Jo 3:3-6); administrar a Igreja com autoridade e dons (1Co 12:7-11); interceder pelos crentes com gemidos inexprimíveis (Rm 8:26)."""
            },
            {
                "numero": "5",
                "titulo": "A Bíblia — Manual de Fé dos Cristãos",
                "versiculo": "Salmos 119:105; 2 Timóteo 3:16",
                "conteudo": """<b>Texto Áureo:</b> <i>"Lâmpada para os meus pés é a tua palavra e luz para o meu caminho."</i> — Sl 119:105<br/><br/>
1. A Bíblia é a Palavra inspirada de Deus (2Tm 3:16). É fiel, nunca falha (Js 23:14), é alimento para a alma (Jr 15:16) e é eterna (Is 40:8). Não se pode conhecer e obedecer a Deus sem conhecer a Sua Palavra.<br/>
2. <b>Escritores:</b> Cerca de 40 homens inspirados, num período aproximado de 1600 anos. O Autor supremo é Deus; o Intérprete é o Espírito Santo; o Tema Central é Jesus Cristo.<br/>
3. <b>Divisão dos 66 Livros:</b><br/>
• <b>Antigo Testamento (39 Livros):</b> Pentateuco (5 livros - Génesis a Deuteronómio), Históricos (12 livros - Josué a Ester), Poéticos (5 livros - Jó a Cantares), Profetas Maiores (5 livros - Isaías a Daniel) e Profetas Menores (12 livros - Oseias a Malaquias).<br/>
• <b>Novo Testamento (27 Livros):</b> Evangelhos (4 livros - Mateus a João), Histórico (1 livro - Actos), Epístolas Paulinas (13 livros - Romanos a Filemon), Epístolas Gerais (8 livros - Hebreus a Judas) e Revelação (1 livro - Apocalipse)."""
            }
        ],
        "questionario": [
            {"id": 1, "pergunta": "Segundo o manual, qual a definição exata de pecar?", "opcoes": ["Errar o alvo da vontade de Deus e transgredir a Sua lei moral.", "Um mero esquecimento sem consequências espirituais."], "correta": 0},
            {"id": 2, "pergunta": "Qual a diferença bíblica entre desobedecer e transgredir?", "opcoes": ["Desobedecer é a causa no coração; transgredir é o efeito exposto exteriormente.", "Não há nenhuma diferença, são termos sem ligação moral."], "correta": 0},
            {"id": 3, "pergunta": "A salvação é concedida por mérito das nossas obras?", "opcoes": ["Não, é alcançada exclusivamente pela graça por meio da fé.", "Sim, é mérito conquistado pelas nossas esmolas e jejuns."], "correta": 0},
            {"id": 4, "pergunta": "Como o mundo aprende melhor a lição transmitida por uma testemunha de Cristo?", "opcoes": ["Observando o que ela faz e o seu bom procedimento diário.", "Apenas ouvindo discursos teóricos e debates calorosos."], "correta": 0},
            {"id": 5, "pergunta": "A Bíblia ensina a existência de três deuses diferentes?", "opcoes": ["Não, ensina Um Só Deus verdadeiro que subsiste em três Pessoas: Pai, Filho e Espírito Santo.", "Sim, ensina três deuses independentes governando em turnos."], "correta": 0},
            {"id": 6, "pergunta": "Qual o significado literal dos nomes Jesus e Cristo?", "opcoes": ["Jesus significa 'O Senhor é Salvador' e Cristo significa 'O Ungido'.", "Jesus significa mestre sábio e Cristo significa líder político."], "correta": 0},
            {"id": 7, "pergunta": "O Espírito Santo possui os atributos exclusivos da divindade?", "opcoes": ["Sim, Ele é Omnipotente, Omnisciente e Omnipresente.", "Não, Ele é apenas uma energia passageira sem mente própria."], "correta": 0},
            {"id": 8, "pergunta": "Quantos livros compõem o cânon bíblico da Igreja Cristã?", "opcoes": ["66 livros (39 no Antigo Testamento e 27 no Novo Testamento).", "73 livros distribuídos igualmente."], "correta": 0}
        ]
    },
    "c2": {
        "nome": "Classe II — Vida Cristã",
        "duracao": "Semanas 7 a 12",
        "ordem": 2,
        "proxima": "c3",
        "licoes": [
            {
                "numero": "1",
                "titulo": "Oração e Jejum",
                "versiculo": "Lucas 2:37; 1 Tessalonicenses 5:17",
                "conteudo": """<b>Texto Áureo:</b> <i>"...servindo a Deus em jejuns e orações, de noite e de dia."</i> — Lc 2:37<br/><br/>
<b>I. A ORAÇÃO:</b><br/>
1. É uma ordem e necessidade vital (Sl 65:2; 1Ts 5:17). As orações sobem diante de Deus como incenso suave (Sl 141:2; Ap 5:8). O Espírito Santo intercede e auxilia nas nossas fraquezas (Rm 8:26,27).<br/>
2. Deus responde a quem O busca com fé e guarda a Sua Palavra (Mt 21:22; 1Jo 3:22), mas não responde a pedidos feitos com maus motivos ou de quem vive na prática do pecado (Tg 4:3; Is 59:2).<br/><br/>
<b>II. O JEJUM:</b><br/>
1. O Jejum bíblico é a abstinência de alimento para dedicar-se à oração e sujeição da carne perante Deus (Zc 7:5; Sl 35:13). Torna o crente espiritualmente mais sensível à voz do Espírito Santo.<br/>
2. O espírito correto do jejum deve ser humilde, secreto e acompanhado de amor e misericórdia prática para com o próximo (Is 58:6,7; Mt 6:16-18)."""
            },
            {
                "numero": "2",
                "titulo": "A Tentação e Como Vencer a Tentação",
                "versiculo": "Tiago 4:7; 1 Coríntios 10:13",
                "conteudo": """<b>Texto Áureo:</b> <i>"Sujeitai-vos, pois, a Deus, resisti ao diabo, e ele fugirá de vós."</i> — Tg 4:7<br/><br/>
1. A tentação provém de nossos próprios desejos carnais, da cobiça e dos ardis do diabo (Tg 1:14; 1Tm 6:9; Mt 4:1). <b>Ter tentação não é pecado; o pecado ocorre ao ceder à tentação.</b><br/>
2. Deus é fiel: não permite tentação além das nossas forças e sempre providencia o escape para que possamos suportar (1Co 10:13; 2Pe 2:9).<br/>
3. <b>Como Vencer:</b> Primeiro, sujeitar-se a Deus (Tg 4:7); examinar as causas evitando companhias impróprias e locais promíscuos (2Co 13:5); nunca buscar soluções na feitiçaria ou curandeirismo; empunhar a Palavra de Deus e manter vigilância em oração (Ef 6:17,18)."""
            },
            {
                "numero": "3",
                "titulo": "A Vontade de Deus",
                "versiculo": "Efésios 6:6; 1 João 2:17",
                "conteudo": """<b>Texto Áureo:</b> <i>"Não servindo à vista, como para agradar aos homens, mas como servos de Cristo, fazendo de coração a vontade de Deus."</i> — Ef 6:6<br/><br/>
1. Fazer a vontade de Deus é o propósito primordial do salvo (1Jo 2:17). Implica renunciar a própria vontade egoísta, ter paciência e perseverar na prática do bem (Hb 10:36; 1Pe 2:15).<br/>
2. <b>A Vontade de Deus é Dupla:</b><br/>
• <b>Geral:</b> Revelada a todos os homens na Bíblia Sagrada (regras fundamentais de conduta e fé - Sl 119:11).<br/>
• <b>Específica:</b> Revelada pessoalmente pelo Espírito Santo aos servos fiéis que oram, jejuam e meditam nas Escrituras (At 13:2; At 9:11)."""
            },
            {
                "numero": "4",
                "titulo": "O Espírito Santo — Baptismo, Fruto, Dons e Símbolos",
                "versiculo": "Atos 1:8; Gálatas 5:22; 1 Coríntios 12:7-11",
                "conteudo": """<b>Texto Áureo:</b> <i>"Mas recebereis a virtude do Espírito Santo, que há-de vir sobre vós; e ser-me-eis testemunhas..."</i> — At 1:8<br/><br/>
1. <b>Baptismo no Espírito Santo:</b> Revestimento sobrenatural de poder para testemunhar ousadamente (At 1:8). Evidencia-se pelo sinal físico inicial de falar noutras línguas conforme o Espírito concede (At 2:4; At 10:44-46). É promessa para todos os crentes.<br/>
2. <b>O Fruto do Espírito:</b> O carácter moral de Cristo manifesto no cristão. É um só fruto em 9 manifestações: <i>Amor, Gozo, Paz, Longanimidade, Benignidade, Bondade, Fé, Mansidão e Temperança</i> (Gl 5:22).<br/>
3. <b>Os Dons Espirituais:</b> Concedidos soberanamente pelo Espírito Santo para a mútua edificação da Igreja (1Co 12:7-11). Dividem-se em dons de Revelação (Sabedoria, Ciência, Discernimento), Poder (Fé, Curas, Milagres) e Inspiração (Profecia, Línguas, Interpretação).<br/>
4. <b>Símbolos Bíblicos:</b> Fogo, Vento, Água, Azeite/Óleo e Pomba."""
            },
            {
                "numero": "5",
                "titulo": "Dízimos e Ofertas",
                "versiculo": "2 Coríntios 9:7; Malaquias 3:10",
                "conteudo": """<b>Texto Áureo:</b> <i>"Cada um contribua segundo propôs no seu coração; não com tristeza, ou por necessidade; porque Deus ama ao que dá com alegria."</i> — 2Co 9:7<br/><br/>
1. <b>O Dízimo (A Décima Parte):</b> Pertence ao Senhor (Lv 27:30; Ml 3:10). Não é um favor humano, mas um acto sagrado de obediência, gratidão e fidelidade económica. A retenção do dízimo é considerada roubo espiritual nas Escrituras (Ml 3:8).<br/>
2. O espírito devorador que atinge a economia só é repreendido pelo Senhor diante da fidelidade do crente nos dízimos e ofertas alçadas (Ml 3:11).<br/>
3. <b>Ofertas Alçadas:</b> Semeadura voluntária dada com alegria, segundo a prosperidade concedida por Deus, para sustentar o avanço missionário e a Casa do Senhor (2Co 8:3; Lc 6:38)."""
            }
        ],
        "questionario": [
            {"id": 1, "pergunta": "Qual deve ser o verdadeiro espírito ao jejuar perante o Senhor?", "opcoes": ["Humildade, busca espiritual sincera e amor compassivo ao próximo.", "Exibição pública de santidade perante as pessoas."], "correta": 0},
            {"id": 2, "pergunta": "Segundo o manual, ser tentado é em si mesmo pecado?", "opcoes": ["Não, ser tentado não é pecado; o pecado acontece quando cedemos à tentação.", "Sim, o simples facto de sofrer tentação já é pecado consumado."], "correta": 0},
            {"id": 3, "pergunta": "Qual é a dupla forma da vontade de Deus descrita na Lição 3?", "opcoes": ["Geral (revelada na Bíblia para todos) e Específica (guiada pelo Espírito Santo).", "Apenas uma vontade oculta e desconhecida sem regras na Bíblia."], "correta": 0},
            {"id": 4, "pergunta": "Qual é o sinal bíblico inicial do Baptismo no Espírito Santo?", "opcoes": ["O falar em línguas estranhas conforme o Espírito Santo concede.", "Ter sensações de desmaio físico ou calafrio emocional."], "correta": 0},
            {"id": 5, "pergunta": "Em quantas virtudes se manifesta o Fruto do Espírito Santo (Gálatas 5:22)?", "opcoes": ["Em 9 manifestações que expressam o caráter de Cristo.", "Em 3 manifestações estritamente materiais."], "correta": 0},
            {"id": 6, "pergunta": "O que representa o dízimo segundo as Escrituras?", "opcoes": ["A décima parte de toda a renda dada a Deus com fidelidade e obediência.", "Uma taxa governamental opcional que só os pastores devem pagar."], "correta": 0}
        ]
    },
    "c3": {
        "nome": "Classe III — Maturidade Cristã",
        "duracao": "Semanas 13 a 18",
        "ordem": 3,
        "proxima": "c4",
        "licoes": [
            {
                "numero": "1",
                "titulo": "Santificação",
                "versiculo": "1 Pedro 1:16; 1 Tessalonicenses 4:3",
                "conteudo": """<b>Texto Áureo:</b> <i>"Sede Santos, como Eu Sou Santo."</i> — 1Pe 1:16<br/><br/>
1. Dois aspectos da Santificação: Aspecto Negativo (afastados do pecado e do espírito corrompido do mundo - Rm 12:2) e Aspecto Positivo (consagrados e achegados a Deus - Hb 10:22). Santificação é a condição indispensável para ver a Deus e a Sua mão operando (Hb 12:14).<br/>
2. <b>Três Estágios da Santificação:</b><br/>
• <i>Instantânea:</i> Do Espírito, no acto da Salvação e Regeneração (1Co 6:11).<br/>
• <i>Progressiva:</i> Da Alma (pensamentos, desejos e sentimentos), no discipulado diário (Cl 1:22).<br/>
• <i>Final:</i> Do Corpo físico, na ressurreição no Arrebatamento glorioso (1Co 15:53)."""
            },
            {
                "numero": "2",
                "titulo": "Heresias",
                "versiculo": "Mateus 24:4; 2 Pedro 2:1",
                "conteudo": """<b>Texto Áureo:</b> <i>"E Jesus respondendo disse-lhes: Acautelai-vos que ninguém vos engane."</i> — Mt 24:4<br/><br/>
1. Heresias são ensinamentos, crenças e doutrinas heréticas opostas à sã doutrina da Palavra de Deus (1Tm 4:1; 2Pe 2:1).<br/>
2. <b>Erros de Movimentos Falsos Denunciados no Manual:</b><br/>
• <i>Catolicismo Romano:</i> Culto a imagens, invocação de santos falecidos, purgatório, infalibilidade papal.<br/>
• <i>Espiritismo:</i> Consulta aos espíritos dos mortos (abominação condenada em Dt 18:10-12); negação da divindade de Cristo.<br/>
• <i>Russelismo (Testemunhas de Jeová):</i> Negam a Trindade, negam a ressurreição corpórea de Cristo e proíbem adoração a Jesus.<br/>
• <i>Sabatismo (Adventismo):</i> Imposição da guarda da lei mosaica e do sábado como condição salvífica.<br/>
• <i>Mormonismo:</i> Criação de outro livro ('Livro de Mórmon') e negação da autoridade exclusiva da Bíblia.<br/>
• <i>Ecumenismo:</i> Mistura perigosa entre salvos e ímpios sem exigir o arrependimento bíblico e o Novo Nascimento (2Co 6:14)."""
            },
            {
                "numero": "3",
                "titulo": "Anjos e Demónios",
                "versiculo": "Hebreus 1:14; Tiago 4:7",
                "conteudo": """<b>Texto Áureo:</b> <i>"Não são porventura todos eles espíritos ministradores, enviados para servir a favor daqueles que hão-de herdar a salvação."</i> — Hb 1:14<br/><br/>
1. <b>Os Anjos:</b> Seres espirituais criados por Deus para adoração, serviço celeste e assistência aos crentes salvos (Sl 103:20; Hb 1:14). A Bíblia proíbe taxativamente prestar culto ou orações a anjos (Cl 2:18; Ap 22:8,9).<br/>
2. <b>Os Demónios:</b> Anjos rebeldes caídos sob a liderança de Satanás (Jd 6; Mt 25:41). Não possuem omnipotência nem omnipresença.<br/>
3. O crente em Cristo não teme feitiçarias, mas deve sujeitar-se a Deus, resistir firmemente ao diabo na fé e repreender o mal em nome de Jesus (Tg 4:7; 1Pe 5:8,9)."""
            },
            {
                "numero": "4",
                "titulo": "Consciência do Corpo",
                "versiculo": "Romanos 12:5; 1 Coríntios 12:12",
                "conteudo": """<b>Texto Áureo:</b> <i>"Assim nós, que somos muitos, somos um só corpo em Cristo, mas individualmente somos membros uns dos outros."</i> — Rm 12:5<br/><br/>
1. A Igreja é o Corpo Vivo de Cristo; cada crente é membro desse organismo espiritual interdependente (1Co 12:12).<br/>
2. <b>Nenhum membro é independente:</b> Ninguém vê uma mão a caminhar sozinha pela rua. Todos os membros necessitam uns dos outros.<br/>
3. Os deveres mútuos: Honrar os irmãos (Rm 12:10), suportar com amor (Ef 4:2), considerar o outro superior a si mesmo e agir de modo que tudo edifique e nunca cause escândalo ao próximo."""
            },
            {
                "numero": "5",
                "titulo": "Fé: Factos, Não Sentimentos",
                "versiculo": "Hebreus 11:1; 2 Coríntios 5:7",
                "conteudo": """<b>Texto Áureo:</b> <i>"Ora, a fé é o firme fundamento das coisas que se esperam e a prova das coisas que não se vêem."</i> — Hb 11:1<br/><br/>
1. O cristão vive por fé firme naquilo que Deus disse, e não guiado por sensações ou sentimentos carnais passageiros (2Co 5:7).<br/>
2. <b>A Ilustração do Comboio:</b><br/>
• <i>A Locomotiva (O FACTO):</i> É a verdade infalível de Deus e da Sua Palavra.<br/>
• <i>O Vagão Central (A FÉ):</i> É a nossa plena confiança na promessa de Deus.<br/>
• <i>O Vagão Traseiro (OS SENTIMENTOS):</i> São as emoções que vêm como resultado natural da obediência.<br/>
O comboio anda com ou sem vagão de sentimentos. Nunca tente colocar o vagão das emoções para empurrar a locomotiva do facto divino!"""
            }
        ],
        "questionario": [
            {"id": 1, "pergunta": "Quais são as três fases da santificação descritas na Lição 1?", "opcoes": ["Instantânea (Espírito), Progressiva (Alma) e Final (Corpo no Arrebatamento).", "Apenas uma santificação passageira que depende das nossas emoções."], "correta": 0},
            {"id": 2, "pergunta": "Por que a doutrina bíblica rejeita a prática do Espiritismo?", "opcoes": ["Porque a consulta aos mortos é abominação contrária à Bíblia (Dt 18:10-12).", "Porque os espíritos não cobram taxas pelas suas consultas."], "correta": 0},
            {"id": 3, "pergunta": "É bíblico render culto, pedir protecção ou acender velas para os Anjos?", "opcoes": ["Não, a Bíblia proíbe adorar anjos; somente a Deus pertence a adoração (Ap 22:9).", "Sim, os anjos devem ser venerados e adorados como intermediários."], "correta": 0},
            {"id": 4, "pergunta": "Como o crente vence as investidas malignas e o medo de feitiçaria?", "opcoes": ["Sujeitando-se a Deus e resistindo firmemente ao diabo na fé em Cristo (Tg 4:7).", "Indo a curandeiros e usando amuletos de proteção no corpo."], "correta": 0},
            {"id": 5, "pergunta": "Qual a verdade ilustrada pelo comboio (Facto, Fé e Sentimentos)?", "opcoes": ["A nossa fé fundamenta-se nos factos da Palavra de Deus e não nas emoções passageiras.", "O crente só deve crer em Deus quando tiver sensações de arrepio."], "correta": 0},
            {"id": 6, "pergunta": "Como membro do Corpo de Cristo, o crente pode viver de forma independente da igreja?", "opcoes": ["Não, somos interdependentes e necessitamos da comunhão dos irmãos no Corpo.", "Sim, cada crente é auto-suficiente e não precisa de congregação."], "correta": 0}
        ]
    },
    "c4": {
        "nome": "Classe IV — Candidatos ao Baptismo",
        "duracao": "Semanas 19 a 24",
        "ordem": 4,
        "proxima": None,
        "licoes": [
            {
                "numero": "Introdução",
                "titulo": "Princípios e Impedimentos para o Baptismo",
                "versiculo": "Marcos 16:16",
                "conteudo": """<b>Princípios da IEAD para o Baptismo nas Águas:</b><br/>
1. O Baptismo nas águas é exclusivamente para os que nasceram de novo mediante a fé viva em Cristo.<br/>
2. <b>Impedimentos Eclesiásticos para o Baptismo:</b><br/>
• Pessoas não salvas ou sem convicção clara do Evangelho.<br/>
• Viver em união marital irregular (não estar casado oficialmente perante as leis civis).<br/>
• Não ter passado devidamente pelo ensino e frequência nas classes de integração e discipulado bíblico."""
            },
            {
                "numero": "1",
                "titulo": "Baptismo nas Águas e Ceia do Senhor",
                "versiculo": "Atos 2:41; 1 Coríntios 11:24-28",
                "conteudo": """<b>Texto Áureo:</b> <i>"De sorte que foram baptizados os que de bom grado receberam a sua palavra."</i> — At 2:41<br/><br/>
<b>I. O BAPTISMO NAS ÁGUAS:</b><br/>
1. É ordenança sagrada cumprida por <b>imersão total em água</b> em nome do Pai, do Filho e do Espírito Santo (Mt 28:19). Simboliza a morte e sepultamento do velho homem pecador e a ressurreição para viver em novidade de vida com Cristo (Rm 6:4; Cl 2:12).<br/><br/>
<b>II. A CEIA DO SENHOR:</b><br/>
1. A segunda ordenança deixada por Jesus para a Sua Igreja (1Co 11:23-26). Os elementos pão e cálice são <i>símbolos santos</i> do corpo e do sangue de Jesus; não há transformação física da substância (rejeição bíblica da transubstanciação).<br/>
2. <b>As Três Dimensões da Ceia:</b><br/>
• <i>Passado (Comemorativa):</i> "Fazei isto em memória de mim" — lembrança da cruz.<br/>
• <i>Presente (Instrutiva):</i> "Examine-se o homem a si mesmo" — comunhão, perdão mútuo e autoexame espiritual consciente (1Co 11:28).<br/>
• <i>Futuro (Inspiradora):</i> "Até que Ele venha" — anúncio bendito do Arrebatamento iminente!"""
            },
            {
                "numero": "2",
                "titulo": "A Igreja do Senhor",
                "versiculo": "Efésios 5:27",
                "conteudo": """<b>Texto Áureo:</b> <i>"Para a apresentar a si mesmo igreja gloriosa, sem mácula, nem ruga, nem coisa semelhante, mas santa e irrepreensível."</i> — Ef 5:27<br/><br/>
1. A palavra <i>Ekklesia</i> significa 'chamados para fora do pecado'. A Igreja é simultaneamente um organismo vivo (o corpo místico de Cristo) e uma organização que actua na comunidade.<br/>
2. A Cabeça Suprema da Igreja é o Senhor Jesus Cristo (Cl 1:18).<br/>
3. <b>Missão Tripla da Igreja:</b> Adorar a Deus em espírito e em verdade (Jo 4:24); Proclamar o Evangelho a todas as nações (Mc 16:15); e Discipular o povo santo nas Sagradas Escrituras."""
            },
            {
                "numero": "3",
                "titulo": "Membrasia e Disciplina da Igreja",
                "versiculo": "1 Coríntios 12:27; Mateus 18:15-18",
                "conteudo": """<b>Texto Áureo:</b> <i>"Vós sois o corpo de Cristo e seus membros em particular."</i> — 1Co 12:27<br/><br/>
1. <b>A Disciplina Eclesiástica:</b> Tem por objectivo santificar a Igreja, restaurar o irmão faltoso e proteger o rebanho do contágio do pecado (Hb 12:6; Gl 6:1). Nunca deve ser exercida com vingança ou ódio (2Ts 3:15).<br/>
2. <b>Passos Bíblicos (Mt 18:15-17):</b><br/>
• <i>1º Passo:</i> Conversa particular fraternal entre o irmão e o ofensor.<br/>
• <i>2º Passo:</i> Acompanhamento de uma ou duas testemunhas sérias de oração.<br/>
• <i>3º Passo:</i> Apresentação do caso ao Pastor Titular e ao Ministério da Igreja para correcção, suspensão ou corte de comunhão se não houver arrependimento sincero."""
            },
            {
                "numero": "4",
                "titulo": "O Essencial — Conduta do Membro da Igreja",
                "versiculo": "1 Coríntios 10:31",
                "conteudo": """<b>Texto Áureo:</b> <i>"Portanto, quer comais quer bebais, ou façais outra qualquer coisa, fazei tudo para a glória de Deus."</i> — 1Co 10:31<br/><br/>
1. <b>O Seu Falar:</b> Palavra temperada, amistosa, cordial; sem calão, sem insultos, sem maledicência ou piadas obscenas (Tt 2:8; Ef 4:29).<br/>
2. <b>O Seu Trajar e Enfeitar:</b> Trajar com honestidade (compatível com os seus recursos sem negócios ilícitos), com moderação e equilíbrio cristão, e com pudor (sem roupas provocantes ou indecentes). O adorno supremo da mulher e do homem cristão é o espírito manso e quieto perante Deus (1Tm 2:9; 1Pe 3:3-5).<br/>
3. <b>Abandono das Obras da Carne:</b> O crente não frequenta discotecas ou bailes promíscuos, rejeita a pornografia, a fornicação, o adultério, o aborto e as práticas idolátricas ou de feitiçaria."""
            },
            {
                "numero": "5",
                "titulo": "Cerimónias da Igreja",
                "versiculo": "Lucas 2:22; Hebreus 13:4",
                "conteudo": """<b>1. Dedicação de Crianças:</b> Apresentação solene das crianças recém-nascidas a Deus para bênção e dedicação pastoral (Lc 2:22; Mc 10:13). Não é baptismo, pois crianças não têm pecado deliberado nem fé pessoal para confessar.<br/>
<b>2. Matrimónio Sagrado:</b> Instituído por Deus como união sagrada, monogâmica e heterossexual permanente entre um homem e uma mulher (Hb 13:4; Mt 19:4-6). A Igreja celebra a bênção dos casamentos legalizados perante as autoridades civis.<br/>
<b>3. Cultos Fúnebres:</b> Realizados com solenidade e consolo da Palavra para anunciar a ressurreição em Cristo e amparar os enlutados sem recurso a cultos aos mortos ou ritos pagãos."""
            },
            {
                "numero": "6",
                "titulo": "A Vinda do Senhor e Sinais dos Tempos",
                "versiculo": "Apocalipse 22:20; 1 Tessalonicenses 4:16-17",
                "conteudo": """<b>Texto Áureo:</b> <i>"Certamente cedo venho. Ámen."</i> — Ap 22:20<br/><br/>
1. <b>O Arrebatamento da Igreja:</b> A vinda de Jesus nas nuvens para resgatar a Sua Noiva santa de forma súbita e gloriosa. Os mortos em Cristo ressuscitarão primeiro e os vivos serão transformados num piscar de olhos (1Ts 4:16,17; 1Co 15:51-53).<br/>
2. <b>Eventos Escatológicos Subsequentes:</b> Tribunal de Cristo e Bodas do Cordeiro no céu; Grande Tribulação na terra; Julgamento das Nações e Reino Milenar com Cristo.<br/>
3. <b>Os Sinais Evidentes do Fim dos Tempos:</b> Explosão do conhecimento e viagens (Dn 12:4), fomes, pestilências, guerras, quebra dos valores morais nas famílias (2Tm 3:1-4), o retorno do povo judeu à terra de Israel e a proliferação da mornidão espiritual na Igreja contemporânea (o espírito de Laodiceia)."""
            }
        ],
        "questionario": [
            {"id": 1, "pergunta": "Qual é a forma bíblica correta do Baptismo nas Águas?", "opcoes": ["Por imersão total do corpo em nome do Pai, do Filho e do Espírito Santo.", "Por aspersão de algumas gotas de água na cabeça sem confissão de fé."], "correta": 0},
            {"id": 2, "pergunta": "Quais são as três lembranças sagradas ministradas na Santa Ceia?", "opcoes": ["Passado (Lembrança da Cruz), Presente (Autoexame) e Futuro (Até que Cristo venha).", "Apenas uma recordação cerimonial de Páscoa sem valor para hoje."], "correta": 0},
            {"id": 3, "pergunta": "Qual é a missão prioritária da Igreja de Deus na Terra?", "opcoes": ["Pregar o Evangelho, adorar a Deus em santidade e discipular as vidas.", "Acumular bens materiais e disputar poder partidário na política."], "correta": 0},
            {"id": 4, "pergunta": "Qual deve ser o primeiro passo bíblico diante de uma ofensa entre irmãos (Mt 18:15)?", "opcoes": ["Falar pessoalmente a sós com o irmão em amor buscando a reconciliação.", "Publicar nas redes sociais e comentar com toda a congregação."], "correta": 0},
            {"id": 5, "pergunta": "Qual é a orientação bíblica do manual quanto ao trajar e enfeitar do crente?", "opcoes": ["Modéstia, pudor, honestidade e prioridade do caráter interior em Cristo.", "Vestir com exibicionismo, imodéstia e seguir cegamente a moda promíscua."], "correta": 0},
            {"id": 6, "pergunta": "Por que na IEAD não se baptizam bebés e crianças recém-nascidas?", "opcoes": ["Porque as crianças são apresentadas a Deus em dedicação, pois o baptismo exige fé e arrependimento conscientes.", "Porque a igreja não aceita a presença de crianças nas reuniões."], "correta": 0},
            {"id": 7, "pergunta": "Qual é o padrão bíblico defendido para a instituição sagrada do Casamento?", "opcoes": ["União monogâmica, indissolúvel e santa entre um homem e uma mulher legalizada civilmente.", "União temporária e livre sem compromisso legal ou espiritual."], "correta": 0},
            {"id": 8, "pergunta": "Qual é a Bendita Esperança reservada para os fiéis em 1 Tessalonicenses 4:16-17?", "opcoes": ["O Arrebatamento triunfal da Igreja para o encontro com o Senhor nos ares.", "A condenação definitiva sem ressurreição corpórea."], "correta": 0}
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
    estilo_tit = ParagraphStyle('Tit', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=22, alignment=1, textColor=colors.HexColor('#b38600'), spaceAfter=14)
    estilo_intro = ParagraphStyle('Intro', parent=estilos['Normal'], fontName='Helvetica', fontSize=11.5, leading=17, alignment=1, textColor=colors.HexColor('#444444'))
    estilo_nome = ParagraphStyle('Nome', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=21, alignment=1, textColor=colors.HexColor('#0d3b66'), spaceAfter=8)
    estilo_detalhes = ParagraphStyle('Detalhes', parent=estilos['Normal'], fontName='Helvetica', fontSize=11, leading=17, alignment=1, textColor=colors.HexColor('#222222'))
    estilo_versiculo = ParagraphStyle('Verso', parent=estilos['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=13, alignment=1, textColor=colors.HexColor('#666666'))

    elementos.append(Paragraph("IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS", estilo_inst))
    elementos.append(Paragraph("MINISTÉRIO DE CHICUQUE – DEPARTAMENTO DE ENSINO BÍBLICO", estilo_sub))
    elementos.append(Paragraph("CERTIFICADO DE CONCLUSÃO DE DISCIPULADO", estilo_tit))

    elementos.append(Paragraph("Certificamos solenemente perante a Igreja de Deus que o(a) irmão(ã)", estilo_intro))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph(f"<b>{str(membro['nome']).upper()}</b>", estilo_nome))

    texto_detalhe = "concluiu com fidelidade, dedicação e aproveitamento exemplar as <b>24 Lições do Manual Oficial de Integração e Batismo</b> (Classes I a IV), demonstrando aprovação nas avaliações fundamentadas na sã doutrina bíblica e na confissão da fé cristã."
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
