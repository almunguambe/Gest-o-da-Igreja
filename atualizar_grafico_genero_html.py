with open('templates/dashboard_membros.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# Substitui o bloco do gráfico de género por uma apresentação completa com métricas
bloco_antigo_genero = r'<div class="bg-slate-800 p-6 rounded-3xl border border-slate-700 space-y-4">\s*<h3 class="text-sm font-black text-white flex items-center gap-2">\s*<span>⚧️</span> Proporção por Género\s*</h3>\s*<div class="h-44 flex items-center justify-center">\s*<canvas id="graficoGenero"></canvas>\s*</div>\s*</div>'

bloco_novo_genero = '''<div class="bg-slate-800 p-6 rounded-3xl border border-slate-700 space-y-4">
                    <h3 class="text-sm font-black text-white flex items-center justify-between">
                        <span class="flex items-center gap-2"><span>⚧️</span> Proporção por Género</span>
                        <span class="text-[11px] text-slate-400 font-normal">Total: {{ d['total'] }}</span>
                    </h3>
                    <div class="h-40 flex items-center justify-center relative">
                        <canvas id="graficoGenero"></canvas>
                    </div>
                    <!-- Indicadores Numéricos & Percentuais -->
                    <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-700/60">
                        <div class="bg-blue-950/40 border border-blue-900/60 p-2.5 rounded-xl text-center">
                            <span class="text-[11px] font-bold text-blue-400 block">👨 Homens</span>
                            <span class="text-lg font-black text-white">{{ d['homens'] }}</span>
                            <span class="text-[10px] text-blue-300 block font-semibold">{{ d['perc_homens'] }}%</span>
                        </div>
                        <div class="bg-pink-950/40 border border-pink-900/60 p-2.5 rounded-xl text-center">
                            <span class="text-[11px] font-bold text-pink-400 block">👩 Mulheres</span>
                            <span class="text-lg font-black text-white">{{ d['mulheres'] }}</span>
                            <span class="text-[10px] text-pink-300 block font-semibold">{{ d['perc_mulheres'] }}%</span>
                        </div>
                    </div>
                </div>'''

conteudo = re.sub(bloco_antigo_genero, bloco_novo_genero, conteudo, flags=re.DOTALL)

with open('templates/dashboard_membros.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard_membros.html atualizado com percentuais e layout de género!")