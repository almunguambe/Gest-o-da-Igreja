import os
import re

# Caminho para o template onde as congregações são listadas
# Geralmente é templates/igrejas.html ou dentro de index.html
caminho_template = None
for arq in ['templates/igrejas.html', 'templates/congregacoes.html', 'templates/index.html']:
    if os.path.exists(arq):
        caminho_template = arq
        break

if not caminho_template:
    # Se não achar um arquivo isolado, criamos um modal/card reutilizável
    caminho_template = 'templates/igrejas.html'

bloco_acoes_censo = """
<!-- FERRAMENTAS DO CENSO POR CONGREGAÇÃO -->
<div class="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2 items-center">
    <button onclick="copiarLinkCenso('{{ ig.nome if ig.nome is defined else (ig[1] if ig is iterable else ig) }}')" 
            class="px-3 py-1.5 bg-blue-50 text-blue-900 hover:bg-blue-100 text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm">
        <i class="fa-solid fa-copy text-blue-600"></i> Copiar Link Censo
    </button>

    <a href="https://api.whatsapp.com/send?text=A%20Paz%20do%20Senhor!%20Participe%20no%20Censo%20Oficial%20da%20nossa%20igreja.%20Preencha%20a%20sua%20ficha%20aqui:%20https://iead-chicuque.onrender.com/censo?igreja={{ (ig.nome if ig.nome is defined else (ig[1] if ig is iterable else ig)) | urlencode }}" 
       target="_blank" 
       class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm">
        <i class="fa-brands fa-whatsapp text-sm"></i> Partilhar no WhatsApp
    </a>
</div>
"""

funcao_javascript = """
<script>
function copiarLinkCenso(nomeIgreja) {
    const url = window.location.origin + '/censo?igreja=' + encodeURIComponent(nomeIgreja);
    navigator.clipboard.writeText(url).then(() => {
        alert('✓ Link do censo para a congregação "' + nomeIgreja + '" copiado com sucesso! Pode colar no WhatsApp.');
    }).catch(err => {
        prompt('Copie o link abaixo:', url);
    });
}
</script>
"""

# Injetar em templates/censo_homologar.html para ter também um painel de controlo de links lá
with open('templates/censo_homologar.html', 'r', encoding='utf-8') as f:
    homologar_html = f.read()

painel_links_rapidos = """
        <!-- PAINEL RÁPIDO DE LINKS DO CENSO -->
        <div class="bg-white rounded-2xl p-5 mb-6 shadow-sm border border-slate-200">
            <h2 class="text-sm font-black text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                <i class="fa-solid fa-share-nodes text-blue-900"></i> Links Oficiais do Censo para Envio
            </h2>
            <p class="text-xs text-slate-500 mb-4">Clique nos botões abaixo para partilhar o link pronto de cada congregação no WhatsApp:</p>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-black text-blue-950 block">IEAD Chicuque (Sede)</span>
                        <span class="text-[10px] text-slate-400">Link geral / Sede</span>
                    </div>
                    <div class="flex gap-2 mt-3">
                        <button onclick="copiarLinkCenso('IEAD Chicuque')" class="flex-1 py-1.5 bg-white border border-slate-300 text-slate-700 text-xs font-bold rounded-lg hover:bg-slate-100">
                            📋 Copiar
                        </button>
                        <a href="https://api.whatsapp.com/send?text=A%20Paz%20do%20Senhor!%20Participe%20no%20Censo%20Oficial%20da%20IEAD%20Chicuque.%20Preencha%20a%20sua%20ficha:%20https://iead-chicuque.onrender.com/censo?igreja=IEAD%20Chicuque" target="_blank" class="px-3 py-1.5 bg-emerald-600 text-white text-xs font-bold rounded-lg hover:bg-emerald-700 flex items-center gap-1">
                            <i class="fa-brands fa-whatsapp"></i> Enviar
                        </a>
                    </div>
                </div>

                <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-black text-blue-950 block">Link Geral (Livre Escolha)</span>
                        <span class="text-[10px] text-slate-400">O membro escolhe a congregação</span>
                    </div>
                    <div class="flex gap-2 mt-3">
                        <button onclick="navigator.clipboard.writeText(window.location.origin + '/censo'); alert('✓ Link geral copiado!');" class="flex-1 py-1.5 bg-white border border-slate-300 text-slate-700 text-xs font-bold rounded-lg hover:bg-slate-100">
                            📋 Copiar
                        </button>
                        <a href="https://api.whatsapp.com/send?text=A%20Paz%20do%20Senhor!%20Participe%20no%20Censo%20Oficial%20da%20nossa%20igreja.%20Preencha%20a%20sua%20ficha:%20https://iead-chicuque.onrender.com/censo" target="_blank" class="px-3 py-1.5 bg-emerald-600 text-white text-xs font-bold rounded-lg hover:bg-emerald-700 flex items-center gap-1">
                            <i class="fa-brands fa-whatsapp"></i> Enviar
                        </a>
                    </div>
                </div>
            </div>
        </div>
"""

if 'PAINEL RÁPIDO DE LINKS DO CENSO' not in homologar_html:
    homologar_html = homologar_html.replace('{% if pendentes %}', painel_links_rapidos + '\n        {% if pendentes %}')
    if 'function copiarLinkCenso' not in homologar_html:
        homologar_html = homologar_html.replace('</body>', funcao_javascript + '\n</body>')
    with open('templates/censo_homologar.html', 'w', encoding='utf-8') as f:
        f.write(homologar_html)
    print("✓ Painel de links com botão WhatsApp adicionado a templates/censo_homologar.html!")

print("✓ Sistema pronto para partilha automática via sistema!")