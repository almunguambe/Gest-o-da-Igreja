with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# Localiza a section inteira da aba de configurações
padrao_aba = r'<section id="aba-configuracoes" class="tab-content space-y-6">.*?</section>'

nova_aba_configuracoes = '''<section id="aba-configuracoes" class="tab-content space-y-6">

    <!-- 1. MÓDULO PROVINCIAL & DISTRITAL DE MOÇAMBIQUE -->
    <div class="bg-white/95 p-6 rounded-3xl card-glow border border-indigo-100 space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
            <div>
                <h3 class="text-base font-black text-slate-900 flex items-center gap-2">
                    <span>🇲🇿</span> Rede de Congregações & Jurisdição Distrital
                </h3>
                <p class="text-xs text-slate-500 font-semibold">Cadastre congregações filiadas agrupadas rigorosamente por Província e Distrito</p>
            </div>
            <span class="text-xs font-bold px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">IEAD Moçambique</span>
        </div>

        <form action="/config/igreja/nova" method="POST" class="grid grid-cols-1 md:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-200">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">1. Província</label>
                <select id="provincia_select" name="provincia" onchange="atualizarDistritosPorProvincia()" required class="w-full h-11 px-3 text-xs border rounded-xl bg-white font-bold text-slate-800">
                    <option value="">-- Escolha a Província --</option>
                    <option value="Inhambane">Inhambane</option>
                    <option value="Gaza">Gaza</option>
                    <option value="Província de Maputo">Província de Maputo</option>
                    <option value="Cidade de Maputo">Cidade de Maputo</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">2. Distrito Oficial</label>
                <select id="distrito_select" name="distrito" required class="w-full h-11 px-3 text-xs border rounded-xl bg-white font-bold text-slate-800">
                    <option value="">-- Selecione a Província Primeiro --</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">3. Nome da Congregação / Bairro</label>
                <input type="text" name="nome" placeholder="Ex: Chicuque Sede, Maxixe..." required class="w-full h-11 px-3 text-xs border rounded-xl bg-white">
            </div>
            <div class="flex items-end">
                <button type="submit" class="w-full h-11 bg-indigo-600 hover:bg-indigo-700 text-white font-black text-xs rounded-xl shadow transition flex items-center justify-center gap-1.5">
                    <span>➕</span> Cadastrar Congregação
                </button>
            </div>
        </form>

        <!-- Lista de Congregações Cadastradas -->
        <div class="overflow-x-auto max-h-48 overflow-y-auto">
            <table class="w-full text-left text-xs">
                <thead class="bg-slate-100 text-slate-600 font-bold border-b">
                    <tr>
                        <th class="p-2.5">Província</th>
                        <th class="p-2.5">Distrito</th>
                        <th class="p-2.5">Congregação / Igreja</th>
                        <th class="p-2.5 text-center">Remover</th>
                    </tr>
                </thead>
                <tbody class="divide-y text-slate-700">
                    {% for ig in lista_igrejas %}
                    <tr>
                        <td class="p-2.5 font-bold text-slate-900">{{ ig['provincia'] }}</td>
                        <td class="p-2.5 font-semibold text-indigo-700">{{ ig['distrito'] }}</td>
                        <td class="p-2.5">{{ ig['nome'] }}</td>
                        <td class="p-2.5 text-center"><a href="/config/igreja/apagar/{{ ig['id'] }}" class="text-rose-600 font-bold hover:underline">✕</a></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="p-3 text-center text-slate-400">Nenhuma congregação distrital cadastrada até o momento.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- 2. PRIMEIRA LINHA: MINISTÉRIOS, CATEGORIAS CAIXA E ZONAS/BAIRROS (ORIGINAIS) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-blue-950 mb-3 pb-2 border-b">Ministérios</h3>
            <form action="/config/departamento/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Novo..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-blue-900 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-52 overflow-y-auto">
                {% for d in lista_deptos %}<li class="py-2 flex justify-between"><span>{{ d['nome'] }}</span><a href="/config/departamento/apagar/{{ d['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-emerald-950 mb-3 pb-2 border-b">Categorias Caixa</h3>
            <form action="/config/categoria/novo" method="POST" class="space-y-2 mb-3 text-xs">
                <div class="flex gap-2">
                    <select name="tipo" class="h-10 px-2 border rounded-xl bg-white w-1/3"><option value="Entrada">Entrada</option><option value="Saída">Saída</option></select>
                    <input type="text" name="nome" placeholder="Nome..." required class="h-10 px-2 border rounded-xl w-2/3">
                </div>
                <button type="submit" class="w-full h-9 bg-emerald-600 text-white font-bold rounded-xl">+ Guardar</button>
            </form>
            <ul class="divide-y text-xs max-h-52 overflow-y-auto">
                {% for c in lista_categorias %}<li class="py-2 flex justify-between"><span>{{ c['tipo'] }}: {{ c['nome'] }}</span><a href="/config/categoria/apagar/{{ c['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-amber-950 mb-3 pb-2 border-b">Zonas & Bairros</h3>
            <form action="/config/zona/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Nova zona..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-amber-600 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-52 overflow-y-auto">
                {% for z in lista_zonas %}<li class="py-2 flex justify-between"><span>{{ z['nome'] }}</span><a href="/config/zona/apagar/{{ z['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>
    </div>

    <!-- 3. SEGUNDA LINHA: 4 NOVOS CARTÕES DE GESTÃO ECLESIÁSTICA -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <!-- Cargos & Posições -->
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-purple-950 mb-3 pb-2 border-b flex items-center justify-between">
                <span>✝️ Cargos Ministeriais</span>
            </h3>
            <form action="/config/cargo/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Ex: Diácono, Presbítero..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-purple-900 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-48 overflow-y-auto">
                {% for cg in lista_cargos %}<li class="py-2 flex justify-between"><span>{{ cg['nome'] }}</span><a href="/config/cargo/apagar/{{ cg['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>

        <!-- Tipos de Cultos -->
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-cyan-950 mb-3 pb-2 border-b flex items-center justify-between">
                <span>⛪ Tipos de Cultos</span>
            </h3>
            <form action="/config/culto/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Ex: Escola Dominical..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-cyan-800 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-48 overflow-y-auto">
                {% for cl in lista_cultos_cfg %}<li class="py-2 flex justify-between"><span>{{ cl['nome'] }}</span><a href="/config/culto/apagar/{{ cl['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>

        <!-- Contas Financeiras & M-Pesa -->
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-teal-950 mb-3 pb-2 border-b flex items-center justify-between">
                <span>💳 Contas & Meios</span>
            </h3>
            <form action="/config/conta/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Ex: M-Pesa, Caixa..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-teal-700 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-48 overflow-y-auto">
                {% for ct in lista_contas %}<li class="py-2 flex justify-between"><span>{{ ct['nome'] }}</span><a href="/config/conta/apagar/{{ ct['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>

        <!-- Atividades da Secretaria -->
        <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
            <h3 class="text-sm font-black uppercase text-rose-950 mb-3 pb-2 border-b flex items-center justify-between">
                <span>📅 Atividades & Planos</span>
            </h3>
            <form action="/config/atividade/novo" method="POST" class="flex gap-2 mb-3">
                <input type="text" name="nome" placeholder="Ex: Cruzada, Batismo..." required class="h-10 px-2 text-xs border rounded-xl w-full">
                <button type="submit" class="bg-rose-700 text-white px-3 font-bold rounded-xl">+</button>
            </form>
            <ul class="divide-y text-xs max-h-48 overflow-y-auto">
                {% for at in lista_atividades_cfg %}<li class="py-2 flex justify-between"><span>{{ at['nome'] }}</span><a href="/config/atividade/apagar/{{ at['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
            </ul>
        </div>
    </div>

</section>'''

conteudo = re.sub(padrao_aba, nova_aba_configuracoes, conteudo, flags=re.DOTALL)

# Inserção do dicionário JavaScript oficial das Províncias e Distritos de Moçambique
script_distritos = """
<script>
const distritosMocambique = {
    "Inhambane": [
        "Funhalouro", "Govuro", "Homoíne", "Inhambane (Cidade)", "Inharrime",
        "Inhassoro", "Jangamo", "Mabote", "Massinga", "Maxixe (Cidade)",
        "Morrumbene", "Panda", "Vilanculos", "Zavala"
    ],
    "Gaza": [
        "Bilene", "Chibuto", "Chicualacuala", "Chigubo", "Chókwè", "Chongoene",
        "Guijá", "Limpopo", "Mabalane", "Manjacaze", "Mapai", "Massangena",
        "Massingir", "Xai-Xai"
    ],
    "Província de Maputo": [
        "Boane", "Magude", "Manhiça", "Marracuene", "Matola", "Matutuíne",
        "Moamba", "Namaacha"
    ],
    "Cidade de Maputo": [
        "KaMpfumo (Distrito 1)", "Nlhamankulu (Distrito 2)", "KaMaxaquene (Distrito 3)",
        "KaMavota (Distrito 4)", "KaMubukwana (Distrito 5)", "KaTembe", "KaNyaka"
    ]
};

function atualizarDistritosPorProvincia() {
    const provSelect = document.getElementById('provincia_select');
    const distSelect = document.getElementById('distrito_select');
    if (!provSelect || !distSelect) return;

    const prov = provSelect.value;
    distSelect.innerHTML = '';

    if (!prov || !distritosMocambique[prov]) {
        distSelect.innerHTML = '<option value="">-- Selecione a Província Primeiro --</option>';
        return;
    }

    distSelect.innerHTML = '<option value="">-- Selecione o Distrito --</option>';
    distritosMocambique[prov].forEach(function(d) {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        distSelect.appendChild(opt);
    });
}
</script>
</body>
"""

if "distritosMocambique" not in conteudo:
    conteudo = conteudo.replace('</body>', script_distritos)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html atualizado com Províncias/Distritos encadeados e os novos 4 cartões!")