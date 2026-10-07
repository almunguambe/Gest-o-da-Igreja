with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. RESTAURAR O BOTÃO RAIO-X NO MENU LATERAL (Abaixo de Membros)
botao_raiox_menu = '''
                         <a href="/secretaria/dashboard_membros" target="_blank" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-black text-amber-300 bg-amber-500/10 border border-amber-500/20 hover:bg-amber-500/20 transition">
                             <span class="text-base">📊</span> <span>Raio-X da Membrezia</span>
                         </a>'''

if '/secretaria/dashboard_membros' not in conteudo:
    alvo_menu = '<button onclick="trocarAba(\'membros\')"'
    # Coloca o botão logo abaixo do botão de Membros
    fim_botao_membros = '</button>'
    pos_membros = conteudo.find(alvo_menu)
    if pos_membros != -1:
        pos_fim = conteudo.find(fim_botao_membros, pos_membros) + len(fim_botao_membros)
        conteudo = conteudo[:pos_fim] + '\n' + botao_raiox_menu + conteudo[pos_fim:]
        print("✓ Botão do Raio-X adicionado com destaque no Menu Lateral!")

# 2. ADICIONAR O BOTÃO RAIO-X TAMBÉM DENTRO DA ABA DE MEMBROS (Junto ao botão Baixar Excel)
botao_raiox_membros_aba = '''
                        <a href="/secretaria/dashboard_membros" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center gap-1.5">
                            <span>📊</span> Raio-X Estatístico
                        </a>'''

alvo_excel = 'Baixar Excel'
if 'Raio-X Estatístico' not in conteudo and alvo_excel in conteudo:
    pos_excel = conteudo.find(alvo_excel)
    pos_btn_fim = conteudo.find('</a>', pos_excel)
    if pos_btn_fim == -1:
        pos_btn_fim = conteudo.find('</button>', pos_excel)
    if pos_btn_fim != -1:
        fim_tag = conteudo.find('>', pos_btn_fim) + 1
        conteudo = conteudo[:fim_tag] + '\n' + botao_raiox_membros_aba + conteudo[fim_tag:]
        print("✓ Botão do Raio-X adicionado na barra da tabela de Membros!")

# 3. ADICIONAR O CARD "TIPOS DE EVENTOS" NAS CONFIGURAÇÕES
card_evento = '''
        <!-- Tipos de Eventos -->
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-amber-950 mb-3 pb-2 border-b flex items-center justify-between">
                <span>🎪 Tipos de Eventos</span>
            </h3>
            <form action="/config/evento/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Ex: Vigília, Retiro..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-amber-600 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-48 overflow-y-auto">
                {% for ev in lista_eventos_cfg %}<li class="py-2 flex justify-between"><span>{{ ev['nome'] }}</span><a href="/config/evento/apagar/{{ ev['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>
'''

if 'Tipos de Eventos' not in conteudo:
    alvo_card = '<!-- Atividades da Secretaria -->'
    if alvo_card in conteudo:
        conteudo = conteudo.replace(alvo_card, card_evento + '\n        ' + alvo_card)
        # Ajusta o grid para comportar mais colunas
        conteudo = conteudo.replace('grid-cols-1 md:grid-cols-4 gap-6', 'grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4')
        print("✓ Card 'Tipos de Eventos' adicionado à aba de Configurações!")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html atualizado com sucesso!")