import os

estudos_path = os.path.join("templates", "estudos.html")

with open(estudos_path, "r", encoding="utf-8") as f:
    html = f.read()

bloco_respostas_aluno = """
        <!-- MURAL DE RESPOSTAS PASTORAIS PARA O ALUNO -->
        {% if minhas_duvidas %}
        <div class="bg-white rounded-3xl p-5 shadow-md border border-indigo-100 space-y-3">
            <h3 class="text-sm font-black text-slate-900 flex items-center gap-2">
                <span>📬</span> <span>Minhas Perguntas & Respostas da Liderança Pastoral</span>
            </h3>
            <div class="space-y-3 max-h-64 overflow-y-auto pr-1">
                {% for md in minhas_duvidas %}
                <div class="p-3.5 bg-slate-50 rounded-2xl border text-xs space-y-2">
                    <div class="flex justify-between items-start">
                        <span class="font-bold text-blue-900">Lição: {{ md['licao'] }}</span>
                        {% if md['resposta'] %}
                        <span class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2 py-0.5 rounded-full">Respondida</span>
                        {% else %}
                        <span class="bg-amber-100 text-amber-800 text-[10px] font-black px-2 py-0.5 rounded-full">Aguardando resposta do Pastor</span>
                        {% endif %}
                    </div>
                    <p class="text-slate-700"><strong>Minha Pergunta:</strong> {{ md['duvida'] }}</p>
                    
                    {% if md['resposta'] %}
                    <div class="p-3 bg-amber-50/80 border border-amber-200 rounded-xl text-amber-950 space-y-1">
                        <strong class="block text-[11px] uppercase tracking-wider text-amber-900 font-black">Orientação do Pastor:</strong>
                        <p class="whitespace-pre-line leading-relaxed">{{ md['resposta'] }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
"""

if "MURAL DE RESPOSTAS PASTORAIS PARA O ALUNO" not in html:
    html = html.replace('<main class="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">', '<main class="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">\n' + bloco_respostas_aluno)

with open(estudos_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✓ templates/estudos.html atualizado para exibir as orientações pastorais ao aluno!")