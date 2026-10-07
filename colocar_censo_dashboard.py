with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Botões no topo ao lado de 'Baixar Excel' e 'Raio-X Estatístico'
botoes_censo = """
            <a href="/admin/censo/homologar" class="inline-flex items-center gap-2 px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-black shadow-md transition" title="Validar Fichas Enviadas">
                <i class="fa-solid fa-clipboard-check text-sm"></i>
                <span>Homologar Censo</span>
            </a>
            <button type="button" onclick="copiarLinkCensoGeral()" class="inline-flex items-center gap-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-black shadow-md transition" title="Copiar Link para Partilhar no WhatsApp">
                <i class="fa-brands fa-whatsapp text-sm"></i>
                <span>Copiar Link Censo</span>
            </button>
"""

# Injetar ao lado do Baixar Excel ou Raio-X
if 'Baixar Excel' in conteudo and 'Homologar Censo' not in conteudo:
    # Insere imediatamente antes ou depois do Baixar Excel
    conteudo = conteudo.replace('Baixar Excel</a>', 'Baixar Excel</a>\n' + botoes_censo)
    print("✓ Botões do censo inseridos ao lado do Baixar Excel!")
elif 'Raio-X Estatístico' in conteudo and 'Homologar Censo' not in conteudo:
    conteudo = conteudo.replace('Raio-X Estatístico</a>', 'Raio-X Estatístico</a>\n' + botoes_censo)
    print("✓ Botões do censo inseridos ao lado do Raio-X Estatístico!")

# 2. Injetar também um item no menu lateral esquerdo se existir no dashboard.html
item_menu_censo = """
                <a href="/admin/censo/homologar" class="flex items-center gap-3 px-4 py-3 text-slate-300 hover:text-white hover:bg-white/10 rounded-2xl transition font-medium text-xs">
                    <i class="fa-solid fa-clipboard-check text-emerald-400 text-base"></i>
                    <span>Censo & Links WhatsApp</span>
                </a>
"""

if '/admin/censo/homologar' not in conteudo:
    # Tenta achar onde tem 'Membros' no menu lateral
    if 'Gestão de Congregações' in conteudo:
        conteudo = conteudo.replace('Gestão de Congregações</a>', 'Gestão de Congregações</a>\n' + item_menu_censo)
        print("✓ Link do Censo inserido na barra lateral!")

# 3. Script para copiar o link direto com um clique
script_copiar = """
<script>
function copiarLinkCensoGeral() {
    const url = window.location.origin + '/censo';
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            alert('✓ LINK DO CENSO COPIADO COM SUCESSO!\\n\\n' + url + '\\n\\nJá pode colar nos grupos de WhatsApp dos membros ou das congregações.');
        }).catch(() => {
            prompt('Copie o link abaixo para enviar aos membros no WhatsApp:', url);
        });
    } else {
        prompt('Copie o link abaixo para enviar aos membros no WhatsApp:', url);
    }
}
</script>
"""

if 'function copiarLinkCensoGeral' not in conteudo:
    conteudo = conteudo.replace('</body>', script_copiar + '\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html atualizado com sucesso!")