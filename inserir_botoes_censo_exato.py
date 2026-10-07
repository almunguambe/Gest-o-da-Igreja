with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

alvo = '<a href="/exportar/membros"'

novos_botoes = """
                            <!-- BOTÕES OFICIAIS DO CENSO -->
                            <a href="/admin/censo/homologar" class="h-10 px-4 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-black shadow transition flex items-center gap-1.5" title="Aprovar e homologar fichas do censo">
                                <span>📋 Homologar Censo</span>
                            </a>
                            <button type="button" onclick="copiarLinkCensoGeral()" class="h-10 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-black shadow transition flex items-center gap-1.5" title="Copiar link para WhatsApp">
                                <span>📱 Link Censo (WhatsApp)</span>
                            </button>
                            <a href="/exportar/membros"
"""

funcao_js = """
<script>
function copiarLinkCensoGeral() {
    const url = window.location.origin + '/censo';
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            alert('✓ LINK DO CENSO COPIADO!\\n\\n' + url + '\\n\\nCole nos grupos de WhatsApp dos membros ou das congregações.');
        }).catch(() => {
            prompt('Copie o link abaixo para enviar aos membros:', url);
        });
    } else {
        prompt('Copie o link abaixo para enviar aos membros:', url);
    }
}
</script>
"""

if alvo in conteudo:
    # Insere imediatamente antes do Baixar Excel
    conteudo = conteudo.replace(alvo, novos_botoes.strip() + '\n                            <a href="/exportar/membros"', 1)
    print("✓ Botões inseridos ao lado do Baixar Excel com sucesso!")
else:
    print("Alvo não encontrado!")

if 'function copiarLinkCensoGeral' not in conteudo:
    conteudo = conteudo.replace('</body>', funcao_js + '\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html salvo com sucesso!")