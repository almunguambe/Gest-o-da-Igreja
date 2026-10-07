with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Atualizar a função JS para ocultar Estado Civil tanto para Criança quanto para Adolescente
js_antigo = """    if (segmentoEl.value === 'Criança') {
        boxEstadoCivil.style.display = 'none';
        if (selectEstadoCivil) selectEstadoCivil.value = 'Solteiro(a)';
    } else {
        boxEstadoCivil.style.display = 'block';
    }"""

js_novo = """    const seg = (segmentoEl.value || '').trim();
    if (seg === 'Criança' || seg === 'Adolescente') {
        boxEstadoCivil.style.display = 'none';
        if (selectEstadoCivil) selectEstadoCivil.value = 'Solteiro(a)';
    } else {
        boxEstadoCivil.style.display = 'block';
    }"""

if js_antigo in conteudo:
    conteudo = conteudo.replace(js_antigo, js_novo)
    print("✓ Condição atualizada: Criança e Adolescente agora ocultam o Estado Civil e fixam 'Solteiro(a)'!")
else:
    # Se a função estiver com ligeira variação de espaçamento, faz substituição por regex
    import re
    padrao = r"function alternarEstadoCivilPorSegmento\(\)\s*\{.*?\}"
    funcao_completa = """function alternarEstadoCivilPorSegmento() {
    const segmentoEl = document.getElementById('select_segmento_membro');
    const boxEstadoCivil = document.getElementById('box-estado-civil');
    const selectEstadoCivil = document.getElementById('select_estado_civil');
    
    if (!segmentoEl || !boxEstadoCivil) return;

    const seg = (segmentoEl.value || '').trim();
    if (seg === 'Criança' || seg === 'Adolescente') {
        boxEstadoCivil.style.display = 'none';
        if (selectEstadoCivil) selectEstadoCivil.value = 'Solteiro(a)';
    } else {
        boxEstadoCivil.style.display = 'block';
    }
}"""
    conteudo = re.sub(padrao, funcao_completa, conteudo, flags=re.DOTALL)
    print("✓ Função alternarEstadoCivilPorSegmento substituída via regex!")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html atualizado com sucesso!")