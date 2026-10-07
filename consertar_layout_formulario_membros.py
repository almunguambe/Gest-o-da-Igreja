with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# Localiza todo o bloco do formulário de cadastro de membro
padrao_form_membro = r'<form action="/membros/novo" method="POST" enctype="multipart/form-data".*?</form>'

# Formulário perfeitamente estruturado em linhas organizadas e responsivas
novo_form_membro = '''<form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-4">
    <!-- Foto do Membro -->
    <div class="flex flex-col items-center justify-center p-3 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl">
        <label for="foto_membro_input" class="cursor-pointer px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center gap-2">
            <span>📷</span> Tirar Foto / Carregar
        </label>
        <input type="file" id="foto_membro_input" name="foto" accept="image/*" class="hidden">
        <span class="text-[11px] text-slate-400 mt-1">Fotografia do membro</span>
    </div>

    <!-- Linha 1: Nome Completo -->
    <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">Nome Completo *</label>
        <input type="text" name="nome" required placeholder="Nome oficial..." class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
    </div>

    <!-- Linha 2: Contacto e Género -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Contacto Telefónico</label>
            <input type="text" name="telefone" placeholder="+258 8..." class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Género</label>
            <select name="genero" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white focus:border-indigo-600">
                <option value="Masculino">Masculino</option>
                <option value="Feminino">Feminino</option>
            </select>
        </div>
    </div>

    <!-- Linha 3: Data de Nascimento e Segmento -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Data Nascimento</label>
            <input type="date" name="data_nasc" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Segmento *</label>
            <select name="segmento" required class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-bold focus:border-indigo-600">
                <option value="Adulto">Adulto</option>
                <option value="Jovem">Jovem</option>
                <option value="Adolescente">Adolescente</option>
                <option value="Criança">Criança</option>
            </select>
        </div>
    </div>

    <!-- Linha 4: Localização e Origem -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Zona Eclesiástica</label>
            <select name="zona" class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white">
                <option value="">-- Selecione a Zona --</option>
                {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Bairro / Residência</label>
            <input type="text" name="bairro" placeholder="Ex: Chicuque Sede..." class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Naturalidade</label>
            <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
        </div>
    </div>

    <!-- Linha 5: Estado Civil e Filiação -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">💍 Estado Civil</label>
            <select name="estado_civil" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-semibold focus:border-indigo-600">
                <option value="Solteiro(a)">Solteiro(a)</option>
                <option value="Casado(a) no Religioso">Casado(a) no Religioso</option>
                <option value="Casado(a) no Civil">Casado(a) no Civil</option>
                <option value="Casado(a) Religioso & Civil">Casado(a) Religioso & Civil</option>
                <option value="Viúvo(a)">Viúvo(a)</option>
                <option value="Divorciado(a)">Divorciado(a)</option>
            </select>
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Filiação (Pai & Mãe)</label>
            <input type="text" name="filiacao" placeholder="Nome dos pais..." class="w-full h-11 px-3 text-sm border-2 rounded-xl focus:border-indigo-600">
        </div>
    </div>

    <!-- Linha 6: Documentação -->
    <div class="grid grid-cols-3 gap-3">
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Tipo Doc.</label>
            <select name="tipo_documento" class="w-full h-11 px-2 text-sm border-2 rounded-xl bg-white">
                <option value="BI">BI</option>
                <option value="Cédula">Cédula</option>
                <option value="Cartão de Eleitor">C. Eleitor</option>
                <option value="Passaporte">Passaporte</option>
                <option value="Outro">Outro</option>
            </select>
        </div>
        <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-700 mb-1">Nº Documento</label>
            <input type="text" name="numero_documento" placeholder="Número de identificação..." class="w-full h-11 px-3 text-sm border-2 rounded-xl font-mono focus:border-indigo-600">
        </div>
    </div>

    <!-- Linha 7: Vida Espiritual & Histórico Eclesiástico -->
    <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
        <span class="text-xs font-black uppercase tracking-wider text-slate-700 block">🕊️ Dados Eclesiásticos & Funções</span>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Ano de Conversão</label>
                <input type="number" min="1930" max="2099" name="ano_conv" placeholder="Ex: 2015" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white focus:border-indigo-600">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Data de Batismo nas Águas</label>
                <input type="date" name="data_batismo" class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white focus:border-indigo-600">
            </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Cargo / Posição Atual *</label>
                <select name="posicao_atual" required class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-bold text-slate-800 focus:border-indigo-600">
                    <option value="Membro em Comunhão">Membro em Comunhão</option>
                    <option value="Novo Convertido">Novo Convertido</option>
                    <option value="Diácono / Diaconisa">Diácono / Diaconisa</option>
                    <option value="Evangelista">Evangelista</option>
                    <option value="Presbítero">Presbítero</option>
                    <option value="Pastor / Mãe Pastora">Pastor / Mãe Pastora</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Departamento *</label>
                <select name="departamento" required class="w-full h-11 px-3 text-sm border-2 rounded-xl bg-white font-bold text-slate-800 focus:border-indigo-600">
                    <option value="Activista">Activista Cristã</option>
                    <option value="Juventude">Juventude Cristã</option>
                    <option value="Boa Esperança">Boa Esperança</option>
                    <option value="Pais">Departamento dos Pais</option>
                    <option value="Mães">Departamento das Mães</option>
                    <option value="Escola Dominical">Escola Dominical</option>
                    <option value="Nenhum / Geral">Nenhum / Geral</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Botão de Gravar -->
    <button type="submit" class="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-black text-sm rounded-2xl shadow-lg transition flex items-center justify-center gap-2">
        <span>💾</span> Gravar Ficha de Membro
    </button>
</form>'''

if re.search(padrao_form_membro, conteudo, flags=re.DOTALL):
    conteudo = re.sub(padrao_form_membro, novo_form_membro, conteudo, count=1, flags=re.DOTALL)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Formulário de membro reconstruído e perfeitamente contido dentro do cartão!")
else:
    print("! Padrão do formulário não encontrado. Vamos verificar o trecho manualmente.")