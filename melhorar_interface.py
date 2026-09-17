import os

os.makedirs("templates", exist_ok=True)

html_code = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>IEAD Chicuque - Gestão Eclesiástica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen antialiased selection:bg-blue-600 selection:text-white">

    <!-- Topbar Institucional Nobre -->
    <header class="bg-gradient-to-r from-blue-950 via-blue-900 to-indigo-950 text-white shadow-lg sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 py-3.5 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-12 h-12 rounded-2xl bg-white p-1 shadow-md flex items-center justify-center flex-shrink-0 ring-2 ring-white/20">
                    <img src="/static/logo.svg?v=2026" alt="IEAD" class="w-full h-full object-contain">
                </div>
                <div>
                    <h1 class="text-sm sm:text-base md:text-lg font-extrabold tracking-tight leading-tight uppercase">Assembleia de Deus</h1>
                    <p class="text-xs text-blue-200 font-medium tracking-wide">Congregação de Chicuque</p>
                </div>
            </div>

            <!-- Perfil & Logout -->
            <div class="flex items-center space-x-2">
                <div class="hidden sm:flex flex-col text-right">
                    <span class="text-xs font-bold text-white leading-none">{{ session['usuario'] }}</span>
                    <span class="text-[11px] text-blue-300 mt-0.5">{{ session['cargo'] }}</span>
                </div>
                <div class="sm:hidden px-2.5 py-1 bg-blue-800/80 rounded-lg border border-blue-700/50 text-[11px] font-bold text-blue-100">
                    {{ session['usuario'] }}
                </div>
                <a href="/logout" class="bg-rose-600/90 hover:bg-rose-600 active:scale-95 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow transition duration-150">
                    Sair
                </a>
            </div>
        </div>

        <!-- Abas de Navegação Estilo App Mobile -->
        <div class="max-w-7xl mx-auto px-2 overflow-x-auto no-scrollbar border-t border-blue-800/40 py-2">
            <nav class="flex space-x-2 text-sm font-semibold whitespace-nowrap">
                {% if pode_cadastro %}
                <button onclick="trocarAba('membros')" id="btn-membros" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 bg-white text-blue-950 font-bold shadow-md">
                    <span>👤</span> <span>Membros ({{ total_membros }})</span>
                </button>
                <button onclick="trocarAba('casamentos')" id="btn-casamentos" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>💍</span> <span>Casamentos</span>
                </button>
                <button onclick="trocarAba('mortes')" id="btn-mortes" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>🕊️</span> <span>Óbitos</span>
                </button>
                {% endif %}

                {% if pode_tesouraria %}
                <button onclick="trocarAba('dashboard')" id="btn-dashboard" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 {% if not pode_cadastro %}bg-white text-blue-950 font-bold shadow-md{% else %}text-blue-200 hover:bg-blue-800/40{% endif %}">
                    <span>📊</span> <span>Painel Financeiro</span>
                </button>
                <button onclick="trocarAba('financeiro')" id="btn-financeiro" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>💰</span> <span>Tesouraria</span>
                </button>
                <button onclick="trocarAba('transferencias')" id="btn-transferencias" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>🔄</span> <span>Transferências</span>
                </button>
                {% endif %}

                {% if e_admin %}
                <button onclick="trocarAba('configuracoes')" id="btn-configuracoes" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>⚙️</span> <span>Zonas & Deptos</span>
                </button>
                <button onclick="trocarAba('usuarios')" id="btn-usuarios" class="tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40">
                    <span>👥</span> <span>Utilizadores</span>
                </button>
                {% endif %}
            </nav>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-3 sm:p-5 lg:p-6 space-y-6">

        {% if pode_cadastro %}
        <!-- ================= ABA MEMBROS ================= -->
        <section id="aba-membros" class="tab-content {% if pode_cadastro %}active{% endif %} space-y-6">
            
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                <!-- Formulário de Registo Moderno -->
                <div class="lg:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    
                    <div class="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
                        <div>
                            <h2 class="text-base sm:text-lg font-bold text-slate-900 tracking-tight">Ficha de Membro</h2>
                            <p class="text-xs text-slate-500 font-medium">Registo cadastral e eclesiástico</p>
                        </div>
                        <span class="bg-blue-50 text-blue-700 text-xs font-bold px-3 py-1 rounded-full border border-blue-100">
                            Oficial
                        </span>
                    </div>

                    <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-5">
                        
                        <!-- Upload Interativo com Foto de Perfil ao Vivo -->
                        <div class="flex flex-col items-center justify-center p-5 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl relative group hover:border-blue-500 transition duration-200">
                            <div class="relative w-24 h-24 mb-3">
                                <img id="previewFoto" src="" alt="" class="hidden w-24 h-24 rounded-full object-cover shadow-md ring-4 ring-white border border-slate-200">
                                <div id="placeholderFoto" class="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-100 to-indigo-100 text-blue-900 flex flex-col items-center justify-center shadow-inner border border-blue-200/60">
                                    <svg class="w-8 h-8 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                    </svg>
                                </div>
                            </div>
                            
                            <label class="cursor-pointer bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold px-4 py-2.5 rounded-xl border border-slate-300 shadow-sm active:scale-95 transition">
                                <span>Tirar Foto / Carregar</span>
                                <input type="file" name="foto" id="inputFoto" accept="image/*" capture="environment" class="hidden" onchange="mostrarPreview(event)">
                            </label>
                            <p class="text-[11px] text-slate-400 font-medium mt-1.5">Toque para abrir a câmara ou ficheiros</p>
                        </div>

                        <!-- 1. DADOS PESSOAIS -->
                        <div class="space-y-3.5 pt-1">
                            <span class="text-xs font-bold uppercase tracking-wider text-blue-950 block border-l-4 border-blue-700 pl-2">
                                1. Dados Pessoais
                            </span>

                            <div>
                                <label class="block text-sm font-semibold text-slate-800 mb-1.5">Nome Completo *</label>
                                <input type="text" name="nome" required placeholder="Digite o nome completo" 
                                       class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Contacto Telefónico</label>
                                    <input type="text" name="telefone" placeholder="+258 84/86/87..." 
                                           class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Género</label>
                                    <select name="genero" class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                        <option value="Masculino">Masculino</option>
                                        <option value="Feminino">Feminino</option>
                                    </select>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Data de Nascimento</label>
                                    <input type="date" name="data_nascimento" 
                                           class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                </div>
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Segmento Etário *</label>
                                    <select name="faixa_etaria" required class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white font-bold text-blue-950 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                        <option value="Adulto">Adulto</option>
                                        <option value="Jovem">Jovem</option>
                                        <option value="Adolescente">Adolescente</option>
                                        <option value="Criança">Criança (Boa Esperança)</option>
                                        <option value="Terceira Idade">Terceira Idade</option>
                                    </select>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" 
                                           class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Bairro / Zona Residencial</label>
                                    <select name="bairro" class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                        <option value="">-- Selecione a Zona --</option>
                                        {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-semibold text-slate-800 mb-1.5">Filiação (Nome do Pai & Mãe)</label>
                                <input type="text" name="filiacao" placeholder="Nome dos pais (especialmente para menores)" 
                                       class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>
                        </div>

                        <!-- 2. DOCUMENTAÇÃO -->
                        <div class="space-y-3.5 pt-2">
                            <span class="text-xs font-bold uppercase tracking-wider text-blue-950 block border-l-4 border-amber-600 pl-2">
                                2. Documento de Identificação
                            </span>

                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <div class="sm:col-span-1">
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Tipo Doc.</label>
                                    <select name="tipo_documento" class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white font-bold text-slate-700">
                                        <option value="BI">B.I.</option>
                                        <option value="Cédula">Cédula</option>
                                        <option value="Cartão de Eleitor">C. Eleitor</option>
                                        <option value="Passaporte">Passaporte</option>
                                        <option value="Nenhum">Sem Documento</option>
                                    </select>
                                </div>
                                <div class="sm:col-span-2">
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Número do Documento</label>
                                    <input type="text" name="numero_documento" placeholder="Ex: 0801000... ou nº da Cédula" 
                                           class="w-full h-12 px-3.5 text-sm sm:text-base font-mono border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                            </div>
                        </div>

                        <!-- 3. VIDA ECLESIÁSTICA -->
                        <div class="space-y-3.5 pt-2">
                            <span class="text-xs font-bold uppercase tracking-wider text-blue-950 block border-l-4 border-indigo-600 pl-2">
                                3. Vida Eclesiástica & Cargos
                            </span>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Ano de Conversão</label>
                                    <input type="number" name="ano_conversao" placeholder="Ex: 2016" min="1930" max="2035" 
                                           class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-semibold text-slate-800 mb-1.5">Data Batismo nas Águas</label>
                                    <input type="date" name="data_batismo" 
                                           class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-blue-950 mb-1.5">Posição / Cargo *</label>
                                    <select name="posicao_atual" required class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white font-bold text-blue-900 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                        <option value="Membro em Comunhão">Membro em Comunhão</option>
                                        <option value="Pastor">Pastor</option>
                                        <option value="Presbítero">Presbítero</option>
                                        <option value="Diácono / Diaconisa">Diácono / Diaconisa</option>
                                        <option value="Evangelista">Evangelista</option>
                                        <option value="Obreiro(a)">Obreiro(a)</option>
                                        <option value="Líder de Célula">Líder de Célula</option>
                                        <option value="Membro em Prova">Membro em Prova</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-blue-950 mb-1.5">Departamento Principal *</label>
                                    <select name="departamento" required class="w-full h-12 px-3 text-sm sm:text-base border border-slate-200 rounded-xl outline-none bg-white font-bold text-indigo-900 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition">
                                        <option value="Activista">Activista</option>
                                        <option value="Juventude">Juventude</option>
                                        <option value="Mulher (Senhoras)">Mulher (Senhoras)</option>
                                        <option value="Boa Esperança (Crianças)">Boa Esperança (Crianças)</option>
                                        <option value="Homens / Obreiros">Homens / Obreiros</option>
                                        <option value="Louvor / Música">Louvor / Música</option>
                                        <option value="Ação Social">Ação Social</option>
                                        <option value="Geral">Geral</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-semibold text-slate-800 mb-1.5">Espaço para Progressões Eclesiásticas</label>
                                <textarea name="progressoes" rows="2" placeholder="Histórico de consagrações e promoções ministeriais..." 
                                          class="w-full p-3 text-sm border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white"></textarea>
                            </div>

                            <div>
                                <label class="block text-sm font-semibold text-slate-800 mb-1.5">Observações Adicionais</label>
                                <input type="text" name="observacoes" placeholder="Notas pastorais ou histórico..." 
                                       class="w-full h-12 px-3.5 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>
                        </div>

                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-blue-950 via-blue-900 to-indigo-900 hover:from-blue-900 hover:to-indigo-950 active:scale-[0.99] text-white font-bold text-base rounded-2xl shadow-lg shadow-blue-900/25 transition duration-200 flex items-center justify-center space-x-2">
                            <span>Gravar Ficha de Membro</span>
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        </button>
                    </form>
                </div>

                <!-- Tabela de Membros com Cartão Executivo -->
                <div class="lg:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6 flex flex-col justify-between">
                    <div>
                        <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 mb-5 pb-4 border-b border-slate-100">
                            <div>
                                <h3 class="text-base sm:text-lg font-bold text-slate-900">Membros Registados</h3>
                                <p class="text-xs text-slate-500">Arquivo digital da congregação</p>
                            </div>
                            <div class="flex items-center gap-2">
                                <a href="/exportar/membros" class="h-11 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs sm:text-sm font-bold shadow-sm transition flex items-center gap-1.5 active:scale-95">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                    <span>Exportar Excel</span>
                                </a>
                            </div>
                        </div>

                        <!-- Barra de Pesquisa Rápida -->
                        <div class="mb-4">
                            <div class="relative">
                                <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-400">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                                </span>
                                <input type="text" id="filtroMembros" onkeyup="filtrarTabela('filtroMembros', 'tabelaMembros')" 
                                       placeholder="Pesquisar por nome, BI, cargo, ministério..." 
                                       class="w-full h-12 pl-11 pr-4 text-sm sm:text-base border border-slate-200 rounded-xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>
                        </div>

                        <!-- Lista Responsiva com Cartão/Tabela -->
                        <div class="overflow-x-auto max-h-[640px] rounded-2xl border border-slate-100">
                            <table id="tabelaMembros" class="w-full text-left text-sm min-w-[620px]">
                                <thead class="bg-slate-50 text-slate-700 font-bold border-b border-slate-200 sticky top-0 z-10 text-xs uppercase tracking-wider">
                                    <tr>
                                        <th class="p-3.5">Membro</th>
                                        <th class="p-3.5">Posição / Cargo</th>
                                        <th class="p-3.5">Departamento</th>
                                        <th class="p-3.5">Documento</th>
                                        <th class="p-3.5 text-center">Ficha</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100 text-slate-700">
                                    {% for m in todos_membros %}
                                    <tr class="hover:bg-blue-50/40 transition">
                                        <td class="p-3.5 flex items-center space-x-3">
                                            {% if m['foto_path'] %}
                                            <img src="{{ m['foto_path'] }}" class="w-12 h-12 object-cover rounded-2xl border-2 border-white shadow-sm ring-1 ring-slate-200">
                                            {% else %}
                                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-100 to-indigo-100 text-blue-900 flex items-center justify-center font-black text-sm border border-blue-200 shadow-inner">
                                                {{ m['nome'][:2].upper() }}
                                            </div>
                                            {% endif %}
                                            <div>
                                                <span class="font-bold text-slate-900 block text-sm sm:text-base leading-tight">{{ m['nome'] }}</span>
                                                <span class="text-xs text-slate-500 font-medium block mt-0.5">{{ m['faixa_etaria'] or 'Adulto' }} • {{ m['telefone'] or 'Sem contacto' }}</span>
                                            </div>
                                        </td>
                                        <td class="p-3.5">
                                            <span class="bg-blue-50 border border-blue-100 text-blue-900 font-bold px-3 py-1 rounded-lg text-xs inline-block">
                                                {{ m['posicao_atual'] or 'Membro' }}
                                            </span>
                                            {% if m['progressoes'] %}
                                            <span class="text-[11px] text-indigo-700 font-semibold block mt-1 truncate max-w-[150px]" title="{{ m['progressoes'] }}">📈 {{ m['progressoes'] }}</span>
                                            {% endif %}
                                        </td>
                                        <td class="p-3.5">
                                            <span class="px-2.5 py-1 rounded-lg text-xs font-bold inline-block
                                                {% if m['departamento'] == 'Activista' %}bg-amber-100 text-amber-900 border border-amber-200
                                                {% elif m['departamento'] == 'Juventude' %}bg-purple-100 text-purple-900 border border-purple-200
                                                {% elif m['departamento'] == 'Mulher (Senhoras)' %}bg-rose-100 text-rose-900 border border-rose-200
                                                {% elif m['departamento'] == 'Boa Esperança (Crianças)' %}bg-emerald-100 text-emerald-900 border border-emerald-200
                                                {% else %}bg-slate-100 text-slate-800 border border-slate-200{% endif %}">
                                                {{ m['departamento'] or 'Geral' }}
                                            </span>
                                        </td>
                                        <td class="p-3.5 font-mono text-xs text-slate-600">
                                            <strong>{{ m['tipo_documento'] or 'BI' }}:</strong> {{ m['numero_documento'] or '-' }}
                                        </td>
                                        <td class="p-3.5 text-center whitespace-nowrap">
                                            <button onclick="verCartaoMembro({{ m['id'] }})" class="bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 font-bold px-3 py-1.5 rounded-xl text-xs shadow-sm transition active:scale-95 mr-1">
                                                Visualizar
                                            </button>
                                            {% if e_admin %}
                                            <a href="/apagar/membro/{{ m['id'] }}" onclick="return confirm('Eliminar o membro definitivamente?');" class="text-rose-600 hover:text-rose-800 font-bold text-xs p-1">
                                                ✕
                                            </a>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- ================= ABA CASAMENTOS ================= -->
        <section id="aba-casamentos" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="lg:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Registo Matrimonial</h3>
                    <form action="/casamentos/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold mb-1">Nome do Noivo *</label>
                            <input type="text" name="noivo" required placeholder="Nome do noivo" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Nome da Noiva *</label>
                            <input type="text" name="noiva" required placeholder="Nome da noiva" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Data da Celebração *</label>
                            <input type="date" name="data_casamento" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Pastor Oficiante</label>
                            <input type="text" name="pastor_oficiante" placeholder="Ministro que realizou o ato" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <button type="submit" class="w-full h-12 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl shadow-md transition">
                            Gravar Registo Matrimonial
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Livro de Casamentos</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-600 text-xs uppercase border-b">
                                <tr><th class="p-3">Data</th><th class="p-3">Casal</th><th class="p-3">Oficiante</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {% for c in todos_casamentos %}
                                <tr>
                                    <td class="p-3 font-semibold">{{ c['data_casamento'] }}</td>
                                    <td class="p-3 font-bold text-blue-950">{{ c['noivo'] }} & {{ c['noiva'] }}</td>
                                    <td class="p-3 text-slate-600">{{ c['pastor_oficiante'] or '-' }}</td>
                                    {% if e_admin %}
                                    <td class="p-3 text-center"><a href="/apagar/casamento/{{ c['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a></td>
                                    {% endif %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= ABA ÓBITOS ================= -->
        <section id="aba-mortes" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="lg:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Registo de Óbito</h3>
                    <form action="/mortes/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold mb-1">Nome do Falecido *</label>
                            <input type="text" name="nome_falecido" required placeholder="Nome completo" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Data do Falecimento *</label>
                            <input type="date" name="data_falecimento" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Observações / Notas</label>
                            <input type="text" name="observacoes" placeholder="Local, dados adicionais..." class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none focus:border-blue-600">
                        </div>
                        <button type="submit" class="w-full h-12 bg-slate-900 hover:bg-black text-white font-bold rounded-xl shadow-md transition">
                            Gravar Registo de Óbito
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Livro de Falecimentos</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-600 text-xs uppercase border-b">
                                <tr><th class="p-3">Data</th><th class="p-3">Falecido</th><th class="p-3">Observações</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {% for m in todas_mortes %}
                                <tr>
                                    <td class="p-3 font-semibold">{{ m['data_falecimento'] }}</td>
                                    <td class="p-3 font-bold text-slate-900">{{ m['nome_falecido'] }}</td>
                                    <td class="p-3 text-slate-500">{{ m['observacoes'] or '-' }}</td>
                                    {% if e_admin %}
                                    <td class="p-3 text-center"><a href="/apagar/morte/{{ m['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a></td>
                                    {% endif %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>
        {% endif %}

        {% if pode_tesouraria %}
        <!-- ================= ABA DASHBOARD FINANCEIRO ================= -->
        <section id="aba-dashboard" class="tab-content {% if not pode_cadastro and pode_tesouraria %}active{% endif %} space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <span class="text-xs font-bold uppercase text-amber-700 block">💵 Caixa Físico</span>
                    <p class="text-2xl sm:text-3xl font-black text-amber-900 mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_caixa) }} <span class="text-sm font-bold text-slate-500">MT</span></p>
                </div>
                <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200/80">
                    <span class="text-xs font-bold uppercase text-indigo-700 block">🏛️ Conta Bancária</span>
                    <p class="text-2xl sm:text-3xl font-black text-indigo-900 mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_banco) }} <span class="text-sm font-bold text-slate-500">MT</span></p>
                </div>
                <div class="bg-gradient-to-br from-blue-900 to-indigo-950 text-white p-5 rounded-3xl shadow-md border border-blue-800">
                    <span class="text-xs font-bold uppercase text-blue-200 block">🏦 Saldo Total Consolidado</span>
                    <p class="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_total) }} <span class="text-sm font-semibold text-blue-200">MT</span></p>
                </div>
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <span class="text-xs font-bold uppercase text-slate-500 block">👥 Membresia Registada</span>
                    <p class="text-2xl sm:text-3xl font-black text-slate-900 mt-2 tracking-tight">{{ total_membros }} <span class="text-sm font-medium text-slate-400">membros</span></p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 mb-4">Finanças Mensais (Entradas vs Saídas)</h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoEvolucaoMensal"></canvas></div>
                </div>
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 mb-4">Membros por Departamento</h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoDeptos"></canvas></div>
                </div>
            </div>
        </section>

        <!-- ================= ABA TRANSFERENCIAS ================= -->
        <section id="aba-transferencias" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="lg:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Transferência entre Contas</h3>
                    <form action="/financeiro/transferir" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold mb-1">Data *</label>
                            <input type="date" name="data_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <div class="p-3.5 bg-rose-50 border border-rose-100 rounded-2xl space-y-2">
                            <span class="text-xs font-bold text-rose-800 uppercase block">Origem dos Fundos</span>
                            <select name="origem_local" class="w-full h-11 px-3 text-sm border rounded-xl bg-white"><option value="Caixa">Caixa Físico</option><option value="Banco">Conta Bancária</option></select>
                            <select name="origem_depto" class="w-full h-11 px-3 text-sm border rounded-xl bg-white"><option value="Geral">Fundo Geral</option>{% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}</select>
                        </div>
                        <div class="p-3.5 bg-emerald-50 border border-emerald-100 rounded-2xl space-y-2">
                            <span class="text-xs font-bold text-emerald-800 uppercase block">Destino dos Fundos</span>
                            <select name="destino_local" class="w-full h-11 px-3 text-sm border rounded-xl bg-white"><option value="Banco">Conta Bancária</option><option value="Caixa">Caixa Físico</option></select>
                            <select name="destino_depto" class="w-full h-11 px-3 text-sm border rounded-xl bg-white"><option value="Geral">Fundo Geral</option>{% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}</select>
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Valor da Transferência (MT) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="0.00" class="w-full h-12 px-3.5 text-base font-bold border rounded-xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Motivo *</label>
                            <input type="text" name="motivo" required placeholder="Justificação da transferência" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-12 bg-cyan-700 hover:bg-cyan-800 text-white font-bold rounded-xl shadow-md transition">
                            Efetuar Transferência
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Histórico de Transferências</h3>
                    <div class="overflow-x-auto max-h-[500px]">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-600 text-xs uppercase border-b">
                                <tr><th class="p-3">Data</th><th class="p-3">De</th><th class="p-3">Para</th><th class="p-3">Motivo</th><th class="p-3 text-right">Valor</th></tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {% for t in ultimas_transferencias %}
                                <tr>
                                    <td class="p-3">{{ t['data_movimento'] }}</td>
                                    <td class="p-3 font-bold text-rose-700">{{ t['origem_local'] }}</td>
                                    <td class="p-3 font-bold text-emerald-700">{{ t['destino_local'] }}</td>
                                    <td class="p-3 text-slate-600">{{ t['motivo'] }}</td>
                                    <td class="p-3 text-right font-black text-blue-900">{{ "{:,.2f}".format(t['valor']) }} MT</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= ABA TESOURARIA ================= -->
        <section id="aba-financeiro" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="lg:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Lançamento de Caixa</h3>
                    <form action="/financeiro/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold mb-1">Data *</label>
                            <input type="date" name="data_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-sm font-semibold mb-1">Tipo</label>
                                <select name="tipo" id="selectTipoTransacao" onchange="atualizarCategoriasPorTipo()" class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl bg-white font-bold">
                                    <option value="Entrada">Entrada (+)</option>
                                    <option value="Saída">Saída (-)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-semibold mb-1">Conta *</label>
                                <select name="local_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl bg-white font-bold">
                                    <option value="Caixa">Caixa Físico</option>
                                    <option value="Banco">Banco</option>
                                </select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-sm font-semibold mb-1">Fundo / Depto</label>
                                <select name="departamento" class="w-full h-12 px-3 text-sm border rounded-xl bg-white">
                                    <option value="Geral">Geral</option>
                                    {% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-semibold mb-1">Categoria</label>
                                <select name="categoria" id="selectCategoriaTransacao" class="w-full h-12 px-3 text-sm border rounded-xl bg-white"></select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Valor (MT) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="0.00" class="w-full h-12 px-3.5 text-base font-bold border rounded-xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Descrição</label>
                            <input type="text" name="descricao" required placeholder="Detalhes do movimento" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-md transition">
                            Gravar Lançamento
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 pb-3 border-b border-slate-100">
                        <h3 class="text-base sm:text-lg font-bold text-slate-900">Movimentos Financeiros</h3>
                        <a href="/exportar/financeiro" class="h-10 px-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm transition flex items-center gap-1">
                            <span>📥 Exportar Excel</span>
                        </a>
                    </div>
                    <div class="overflow-x-auto max-h-[520px]">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-600 text-xs uppercase border-b sticky top-0">
                                <tr><th class="p-3">Data</th><th class="p-3">Tipo</th><th class="p-3">Conta</th><th class="p-3">Categoria</th><th class="p-3">Descrição</th><th class="p-3 text-right">Valor</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {% for f in todas_financas %}
                                <tr>
                                    <td class="p-3 font-semibold">{{ f['data_movimento'] }}</td>
                                    <td class="p-3"><span class="px-2.5 py-0.5 rounded-full text-xs font-bold {{ 'bg-emerald-100 text-emerald-800' if f['tipo'] == 'Entrada' else 'bg-rose-100 text-rose-800' }}">{{ f['tipo'] }}</span></td>
                                    <td class="p-3 font-bold">{{ f['local_movimento'] }}</td>
                                    <td class="p-3">{{ f['categoria'] }}</td>
                                    <td class="p-3 text-slate-500">{{ f['descricao'] }}</td>
                                    <td class="p-3 text-right font-black {{ 'text-emerald-700' if f['tipo'] == 'Entrada' else 'text-rose-700' }}">{{ "{:,.2f}".format(f['valor']) }} MT</td>
                                    {% if e_admin %}
                                    <td class="p-3 text-center"><a href="/apagar/financeiro/{{ f['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a></td>
                                    {% endif %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>
        {% endif %}

        {% if e_admin %}
        <!-- ================= ABA CONFIGURAÇÕES ================= -->
        <section id="aba-configuracoes" class="tab-content space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <h3 class="text-sm font-bold uppercase text-blue-950 mb-3 pb-2 border-b">1. Ministérios / Departamentos</h3>
                    <form action="/config/departamento/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Novo departamento" required class="h-11 px-3 text-sm border rounded-xl w-full outline-none">
                        <button type="submit" class="bg-blue-950 text-white px-4 font-bold rounded-xl">+</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for d in lista_deptos %}<li class="py-2.5 flex justify-between"><span>{{ d['nome'] }}</span><a href="/config/departamento/apagar/{{ d['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <h3 class="text-sm font-bold uppercase text-emerald-900 mb-3 pb-2 border-b">2. Categorias Financeiras</h3>
                    <form action="/config/categoria/novo" method="POST" class="space-y-2 mb-3 text-sm">
                        <div class="flex gap-2">
                            <select name="tipo" class="h-11 px-2 border rounded-xl bg-white w-1/3 text-xs font-bold"><option value="Entrada">Entrada</option><option value="Saída">Saída</option></select>
                            <input type="text" name="nome" placeholder="Nome" required class="h-11 px-3 border rounded-xl w-2/3 outline-none">
                        </div>
                        <button type="submit" class="w-full h-10 bg-emerald-700 text-white font-bold rounded-xl">+ Adicionar</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for c in lista_categorias %}<li class="py-2.5 flex justify-between"><span><strong>{{ c['tipo'] }}</strong> - {{ c['nome'] }}</span><a href="/config/categoria/apagar/{{ c['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-200/80">
                    <h3 class="text-sm font-bold uppercase text-amber-900 mb-3 pb-2 border-b">3. Zonas & Bairros</h3>
                    <form action="/config/zona/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Nova zona" required class="h-11 px-3 text-sm border rounded-xl w-full outline-none">
                        <button type="submit" class="bg-amber-600 text-white px-4 font-bold rounded-xl">+</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for z in lista_zonas %}<li class="py-2.5 flex justify-between"><span>{{ z['nome'] }}</span><a href="/config/zona/apagar/{{ z['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
            </div>
        </section>

        <!-- ================= ABA UTILIZADORES ================= -->
        <section id="aba-usuarios" class="tab-content space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                <div class="md:col-span-5 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">👤 Criar Novo Acesso</h3>
                    <form action="/usuarios/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold mb-1">Nome de Utilizador (Login) *</label>
                            <input type="text" name="usuario" required placeholder="Ex: secretaria" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Palavra-passe *</label>
                            <input type="password" name="senha" required placeholder="••••••••" class="w-full h-12 px-3.5 text-sm sm:text-base border rounded-xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-semibold mb-1">Nível de Acesso (Cargo) *</label>
                            <select name="cargo" required class="w-full h-12 px-3 text-sm sm:text-base border rounded-xl bg-white font-bold">
                                <option value="Secretário">Secretário (Apenas Cadastro de Membros e Eventos)</option>
                                <option value="Líder">Líder de Ministério (Apenas Cadastro)</option>
                                <option value="Tesoureiro">Tesoureiro (Apenas Tesouraria e Dashboard)</option>
                                <option value="Pastor">Pastor (Administrador / Acesso Total)</option>
                            </select>
                        </div>
                        <button type="submit" class="w-full h-12 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow-md transition">
                            Criar Utilizador
                        </button>
                    </form>
                </div>
                <div class="md:col-span-7 bg-white rounded-3xl shadow-sm border border-slate-200/80 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">Utilizadores Registados</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-50 text-slate-600 text-xs uppercase border-b">
                                <tr><th class="p-3">Login</th><th class="p-3">Cargo / Acesso</th><th class="p-3 text-center">Ação</th></tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                {% for u in lista_usuarios %}
                                <tr>
                                    <td class="p-3 font-bold text-slate-900">{{ u['usuario'] }}</td>
                                    <td class="p-3">
                                        <span class="px-2.5 py-1 rounded-lg text-xs font-bold inline-block 
                                            {% if 'Pastor' in u['cargo'] %}bg-blue-100 text-blue-900
                                            {% elif 'Tesoureiro' in u['cargo'] %}bg-emerald-100 text-emerald-900
                                            {% else %}bg-amber-100 text-amber-900{% endif %}">
                                            {{ u['cargo'] }}
                                        </span>
                                    </td>
                                    <td class="p-3 text-center">
                                        {% if u['usuario'] != 'admin' %}<a href="/usuarios/apagar/{{ u['id'] }}" onclick="return confirm('Eliminar utilizador?');" class="text-rose-600 font-bold">✕</a>
                                        {% else %}<span class="text-slate-400 text-xs font-bold">Principal</span>{% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>
        {% endif %}

    </main>

    <!-- Modal Ficha de Membro com Design Nobre -->
    <div id="modalMembro" class="fixed inset-0 bg-slate-950/70 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl relative border border-slate-200 animate-in fade-in zoom-in duration-200">
            <button onclick="fecharModalMembro()" class="absolute top-5 right-5 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold text-base flex items-center justify-center transition">&times;</button>
            <div id="conteudoModalMembro" class="space-y-4"></div>
        </div>
    </div>

    <script>
        // Pré-visualização da Foto no Formulário
        function mostrarPreview(event) {
            const input = event.target;
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('previewFoto');
                    const placeholder = document.getElementById('placeholderFoto');
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                    placeholder.classList.add('hidden');
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        const membrosDados = {{ membros_json | safe }};

        function verCartaoMembro(id) {
            const m = membrosDados.find(x => x.id === id);
            if (!m) return;

            const fotoHtml = m.foto_path 
                ? `<img src="${m.foto_path}" class="w-28 h-28 object-cover rounded-3xl mx-auto border-4 border-white shadow-lg ring-2 ring-blue-900/20">`
                : `<div class="w-28 h-28 rounded-3xl bg-gradient-to-tr from-blue-100 to-indigo-100 text-blue-950 flex items-center justify-center text-3xl font-black mx-auto border-4 border-white shadow-lg ring-2 ring-blue-900/20">${m.nome.substring(0,2).toUpperCase()}</div>`;

            document.getElementById('conteudoModalMembro').innerHTML = `
                <div class="text-center pb-4 border-b border-slate-100">
                    ${fotoHtml}
                    <h3 class="text-lg font-black text-slate-900 mt-3">${m.nome}</h3>
                    <div class="flex justify-center gap-1.5 mt-2 flex-wrap">
                        <span class="bg-blue-900 text-white text-xs font-bold px-3 py-1 rounded-full">${m.posicao_atual || 'Membro'}</span>
                        <span class="bg-indigo-50 text-indigo-800 border border-indigo-100 text-xs font-bold px-3 py-1 rounded-full">${m.departamento || 'Geral'}</span>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3 text-sm text-slate-600 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Segmento</span><strong>${m.faixa_etaria || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Contacto</span><strong>${m.telefone || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Documento</span><strong>${m.tipo_documento || 'BI'}: ${m.numero_documento || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Naturalidade</span><strong>${m.naturalidade || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Bairro / Zona</span><strong>${m.bairro || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Ano Conversão</span><strong>${m.ano_conversao || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Data Batismo</span><strong>${m.data_batismo || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Filiação</span><strong>${m.filiacao || '-'}</strong></div>
                </div>
                <div class="p-3.5 bg-blue-50/60 rounded-2xl border border-blue-100">
                    <span class="text-xs font-bold text-blue-950 uppercase tracking-wider block mb-1">Histórico de Progressões Eclesiásticas</span>
                    <p class="text-slate-800 text-xs whitespace-pre-line leading-relaxed">${m.progressoes || 'Nenhuma alteração de cargo registada até ao momento.'}</p>
                </div>
                <button onclick="window.print()" class="w-full h-12 bg-slate-900 hover:bg-black text-white font-bold text-sm rounded-2xl shadow-md transition flex items-center justify-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                    <span>Imprimir Cartão de Membro</span>
                </button>
            `;
            document.getElementById('modalMembro').classList.remove('hidden');
            document.getElementById('modalMembro').classList.add('flex');
        }

        function fecharModalMembro() {
            document.getElementById('modalMembro').classList.add('hidden');
            document.getElementById('modalMembro').classList.remove('flex');
        }

        const todasCategorias = {{ categorias_json | safe }};

        function atualizarCategoriasPorTipo() {
            const el = document.getElementById('selectTipoTransacao');
            if (!el) return;
            const tipo = el.value;
            const selectCat = document.getElementById('selectCategoriaTransacao');
            selectCat.innerHTML = '';
            const filtradas = todasCategorias.filter(c => c.tipo === tipo);
            filtradas.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.nome;
                opt.textContent = c.nome;
                selectCat.appendChild(opt);
            });
        }
        document.addEventListener('DOMContentLoaded', atualizarCategoriasPorTipo);

        function trocarAba(abaId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.className = 'tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 text-blue-200 hover:bg-blue-800/40';
            });
            const abaAlvo = document.getElementById('aba-' + abaId);
            if (abaAlvo) abaAlvo.classList.add('active');
            const activeBtn = document.getElementById('btn-' + abaId);
            if (activeBtn) activeBtn.className = 'tab-btn px-4 py-2.5 rounded-xl transition flex items-center gap-2 bg-white text-blue-950 font-bold shadow-md';
        }

        function filtrarTabela(inputId, tabelaId) {
            const filtro = document.getElementById(inputId).value.toLowerCase();
            const tr = document.getElementById(tabelaId).getElementsByTagName('tr');
            for (let i = 1; i < tr.length; i++) {
                tr[i].style.display = tr[i].innerText.toLowerCase().includes(filtro) ? '' : 'none';
            }
        }

        {% if pode_tesouraria %}
        new Chart(document.getElementById('graficoEvolucaoMensal').getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                datasets: [
                    { label: 'Entradas', data: {{ evolucao_entradas | safe }}, borderColor: '#059669', borderWidth: 2.5, tension: 0.3, fill: false },
                    { label: 'Saídas', data: {{ evolucao_saidas | safe }}, borderColor: '#e11d48', borderWidth: 2.5, tension: 0.3, fill: false }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        new Chart(document.getElementById('graficoDeptos').getContext('2d'), {
            type: 'bar',
            data: {
                labels: {{ depto_labels | safe }},
                datasets: [{ label: 'Membros', data: {{ depto_valores | safe }}, backgroundColor: '#1e3a8a', borderRadius: 8 }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
        {% endif %}
    </script>
</body>
</html>
"""

with open(os.path.join("templates", "dashboard.html"), "w", encoding="utf-8") as f:
    f.write(html_code)

print("✓ Novo design mobile com tipografia visível e pré-visualização ao vivo gerado!")