import os

# Ficheiro do painel principal (onde aparecem os membros e botões de topo)
caminho = 'templates/index.html'

with open(caminho, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Bloco com o botão destacado para o Censo e links prontos
bloco_censo_topo = '''
        <!-- BOTÃO OFICIAL DO CENSO E LINKS WHATSAPP -->
        <a href="/admin/censo/homologar" class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-black shadow-md transition">
            <i class="fa-solid fa-clipboard-check text-sm"></i>
            <span>Homologar Censo & Links</span>
        </a>
        <button onclick="copiarLinkCensoGeral()" class="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition" title="Copiar Link para WhatsApp">
            <i class="fa-brands fa-whatsapp text-sm"></i>
            <span>Copiar Link Censo</span>
        </button>
'''

script_copiar = '''
<script>
function copiarLinkCensoGeral() {
    const link = window.location.origin + '/censo';
    navigator.clipboard.writeText(link).then(() => {
        alert('✓ Link do Censo copiado:\\n' + link + '\\n\\nJá pode colar nos grupos de WhatsApp dos membros!');
    }).catch(() => {
        prompt('Copie o link abaixo para enviar aos membros:', link);
    });
}
</script>
'''

# Inserir junto aos botões 'Baixar Excel' e 'Raio-X Estatístico'
if 'Baixar Excel' in conteudo:
    conteudo = conteudo.replace('Baixar Excel', 'Baixar Excel\n' + bloco_censo_topo, 1)
    print("✓ Botão inserido junto aos botões de topo dos Membros!")
elif 'Raio-X Estatístico' in conteudo:
    conteudo = conteudo.replace('Raio-X Estatístico', 'Raio-X Estatístico\n' + bloco_censo_topo, 1)
    print("✓ Botão inserido junto ao Raio-X Estatístico!")
else:
    # Insere antes do fecho do body
    conteudo = conteudo.replace('</body>', bloco_censo_topo + '\n</body>')
    print("✓ Botão inserido no corpo da página!")

if 'function copiarLinkCensoGeral' not in conteudo:
    conteudo = conteudo.replace('</body>', script_copiar + '\n</body>')

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Template atualizado com sucesso!")