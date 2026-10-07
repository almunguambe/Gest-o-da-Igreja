with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Garantir que o select de segmento tenha o id e onchange
conteudo = re.sub(
    r'<select[^>]*name=["\']segmento["\'][^>]*>',
    '<select name="segmento" id="select_segmento_membro" onchange="alternarEstadoCivilPorSegmento()" required class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-bold focus:border-indigo-600">',
    conteudo,
    count=1
)

# 2. Localizar o bloco do Estado Civil e garantir id="box-estado-civil" no container
# Substitui o bloco do estado civil com o container blindado
padrao_bloco_ec = r'(<div[^>]*>\s*<label[^>]*>.*?Estado Civil.*?</label>\s*<select[^>]*name=["\']estado_civil["\'][^>]*>.*?</select>\s*</div>)'

bloco_ec_blindado = '''<div id="box-estado-civil">
            <label class="block text-xs font-bold text-slate-700 mb-1">💍 Estado Civil</label>
            <select name="estado_civil" id="select_estado_civil" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-semibold focus:border-indigo-600">
                <option value="Solteiro(a)">Solteiro(a)</option>
                <option value="Casado(a) no Religioso">Casado(a) no Religioso</option>
                <option value="Casado(a) no Civil">Casado(a) no Civil</option>
                <option value="Casado(a) Religioso & Civil">Casado(a) Religioso & Civil</option>
                <option value="Viúvo(a)">Viúvo(a)</option>
                <option value="Divorciado(a)">Divorciado(a)</option>
            </select>
        </div>'''

conteudo = re.sub(padrao_bloco_ec, bloco_ec_blindado, conteudo, count=1, flags=re.DOTALL)

# 3. Remover versões antigas da função para não haver conflito
conteudo = re.sub(r'<script>\s*function alternarEstadoCivilPorSegmento\(\).*?</script>', '', conteudo, flags=re.DOTALL)

# 4. Inserir script com suporte a classes Tailwind (.hidden) e display estilo direto
script_blindado = """
<script>
function alternarEstadoCivilPorSegmento() {
    var selectSeg = document.getElementById('select_segmento_membro');
    var boxEC = document.getElementById('box-estado-civil');
    var selectEC = document.getElementById('select_estado_civil');

    if (!selectSeg || !boxEC) return;

    var valor = (selectSeg.value || '').trim().toLowerCase();

    // Se for Crianca ou Adolescente, oculta completamente
    if (valor.includes('crian') || valor.includes('adolescen')) {
        boxEC.style.display = 'none';
        boxEC.classList.add('hidden');
        if (selectEC) {
            selectEC.value = 'Solteiro(a)';
        }
    } else {
        boxEC.style.display = 'block';
        boxEC.classList.remove('hidden');
    }
}

// Executa ao carregar e adiciona listener nativo
document.addEventListener('DOMContentLoaded', function() {
    alternarEstadoCivilPorSegmento();
    var selectSeg = document.getElementById('select_segmento_membro');
    if (selectSeg) {
        selectSeg.addEventListener('change', alternarEstadoCivilPorSegmento);
    }
});
</script>
</body>
"""

conteudo = conteudo.replace('</body>', script_blindado)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Campo de Estado Civil blindado: Criança e Adolescente agora ocultam o campo instantaneamente!")