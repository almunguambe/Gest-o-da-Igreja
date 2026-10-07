with open('templates/estudos.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

bloco_antigo = """        {% if resultado_teste %}
        <div class="p-4 bg-emerald-50 border-2 border-emerald-300 rounded-2xl shadow text-emerald-950 font-bold text-xs sm:text-sm flex items-center gap-2">
            <span>🎉</span> <span>{{ resultado_teste }}</span>
        </div>
        {% endif %}"""

bloco_modal = """        {% if resultado_teste %}
        <!-- POP-UP MODAL DE RESULTADO DA AVALIAÇÃO -->
        <div id="modal-resultado-avaliacao" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
            <div class="bg-white rounded-3xl shadow-2xl border border-indigo-100 max-w-md w-full p-6 sm:p-8 text-center space-y-5 transform transition-all scale-100 animate-bounceOnce">
                <div class="w-20 h-20 mx-auto rounded-3xl bg-gradient-to-tr from-amber-400 to-yellow-200 flex items-center justify-center shadow-lg shadow-amber-300/50">
                    <span class="text-4xl">🏆</span>
                </div>
                
                <div class="space-y-2">
                    <span class="text-[11px] font-extrabold uppercase tracking-widest text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">Resultado da Avaliação</span>
                    <h3 class="text-xl sm:text-2xl font-black text-slate-900">Parabéns pelo Esforço!</h3>
                    <p class="text-slate-600 text-sm leading-relaxed font-medium">
                        {{ resultado_teste }}
                    </p>
                </div>

                <div class="pt-2">
                    <button type="button" 
                            onclick="document.getElementById('modal-resultado-avaliacao').remove()" 
                            class="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-blue-700 to-indigo-700 hover:from-blue-800 hover:to-indigo-800 text-white font-extrabold text-sm shadow-xl shadow-indigo-600/30 transition transform active:scale-95">
                        Continuar Estudos ➔
                    </button>
                </div>
            </div>
        </div>
        {% endif %}"""

if bloco_antigo in conteudo:
    conteudo = conteudo.replace(bloco_antigo, bloco_modal)
    with open('templates/estudos.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Pop-up Modal restaurado com sucesso em templates/estudos.html!")
else:
    # Caso haja pequenas variações de espaços
    import re
    padrao = r'\{%\s*if resultado_teste\s*%\}.*?\{%\s*endif\s*%\}'
    conteudo = re.sub(padrao, bloco_modal.strip(), conteudo, flags=re.DOTALL)
    with open('templates/estudos.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Pop-up Modal substituído via expressão regular!")