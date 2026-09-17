import os

os.makedirs("templates", exist_ok=True)

html_colorido = """<!DOCTYPE html>
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
        .card-glow { box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.08), 0 8px 10px -6px rgba(30, 58, 138, 0.04); }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-100 via-blue-50/50 to-indigo-50/40 text-slate-900 min-h-screen antialiased selection:bg-blue-600 selection:text-white">

    <!-- Topbar com Gradiente Nobre e Efeito de Vidro -->
    <header class="bg-gradient-to-r from-blue-950 via-indigo-950 to-slate-950 text-white shadow-xl sticky top-0 z-40 border-b border-indigo-500/20">
        <div class="max-w-7xl mx-auto px-4 py-3.5 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-white to-blue-50 p-1.5 shadow-lg flex items-center justify-center flex-shrink-0 ring-2 ring-amber-400/40">
                    <img src="/static/logo.svg?v=2026" alt="IEAD" class="w-full h-full object-contain">
                </div>
                <div>
                    <h1 class="text-sm sm:text-base md:text-lg font-extrabold tracking-tight leading-tight uppercase text-white flex items-center gap-1.5">
                        Assembleia de Deus
                        <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    </h1>
                    <p class="text-xs text-indigo-200 font-semibold tracking-wide">Congregação de Chicuque • Gestão Integrada</p>
                </div>
            </div>

            <!-- Perfil & Botão Sair Estilizado -->
            <div class="flex items-center space-x-2.5">
                <div class="hidden sm:flex flex-col text-right pr-1">
                    <span class="text-xs font-black text-white leading-none tracking-wide">{{ session['usuario'] }}</span>
                    <span class="text-[11px] text-amber-300 font-bold mt-0.5">{{ session['cargo'] }}</span>
                </div>
                <div class="sm:hidden px-2.5 py-1 bg-indigo-900/80 rounded-xl border border-indigo-400/30 text-[11px] font-bold text-amber-300">
                    {{ session['usuario'] }}
                </div>
                <a href="/logout" class="bg-gradient-to-r from-rose-500 to-red-600 hover:from-rose-600 hover:to-red-700 active:scale-95 text-white text-xs font-extrabold px-3.5 py-2 rounded-xl shadow-md shadow-rose-900/30 transition duration-150 flex items-center gap-1">
                    <span>Sair</span>
                </a>
            </div>
        </div>

        <!-- Abas com Cores Vivas e Ícones Destacados -->
        <div class="max-w-7xl mx-auto px-3 overflow-x-auto no-scrollbar border-t border-white/10 py-2.5 bg-black/10">
            <nav class="flex space-x-2 text-sm font-semibold whitespace-nowrap">
                {% if pode_cadastro %}
                <button onclick="trocarAba('membros')" id="btn-membros" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black shadow-md shadow-blue-900/40">
                    <span>👤</span> <span>Membros ({{ total_membros }})</span>
                </button>
                <button onclick="trocarAba('casamentos')" id="btn-casamentos" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-indigo-100 hover:bg-white/10 hover:text-white">
                    <span>💍</span> <span>Casamentos</span>
                </button>
                <button onclick="trocarAba('mortes')" id="btn-mortes" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-indigo-100 hover:bg-white/10 hover:text-white">
                    <span>🕊️</span> <span>Óbitos</span>
                </button>
                {% endif %}

                {% if pode_tesouraria %}
                <button onclick="trocarAba('dashboard')" id="btn-dashboard" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 {% if not pode_cadastro %}bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black shadow-md{% else %}text-indigo-100 hover:bg-white/10 hover:text-white{% endif %}">
                    <span>📊</span> <span>Painel Financeiro</span>
                </button>
                <button onclick="trocarAba('financeiro')" id="btn-financeiro" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-indigo-100 hover:bg-white/10 hover:text-white">
                    <span>💰</span> <span>Tesouraria</span>
                </button>
                <button onclick="trocarAba('transferencias')" id="btn-transferencias" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-cyan-300 hover:bg-white/10">
                    <span>🔄</span> <span>Transferências</span>
                </button>
                {% endif %}

                {% if e_admin %}
                <button onclick="trocarAba('configuracoes')" id="btn-configuracoes" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-amber-300 hover:bg-white/10">
                    <span>⚙️</span> <span>Zonas & Deptos</span>
                </button>
                <button onclick="trocarAba('usuarios')" id="btn-usuarios" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-emerald-300 hover:bg-white/10">
                    <span>👥</span> <span>Utilizadores</span>
                </button>
                {% endif %}
            </nav>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-3.5 sm:p-5 lg:p-6 space-y-6">

        {% if pode_cadastro %}
        <!-- ================= ABA MEMBROS ================= -->
        <section id="aba-membros" class="tab-content {% if pode_cadastro %}active{% endif %} space-y-6">
            
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                <!-- Formulário com Cores Vivas -->
                <div class="lg:col-span-5 bg-white/95 backdrop-blur-sm rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    
                    <div class="flex items-center justify-between pb-4 mb-5 border-b border-indigo-50">
                        <div>
                            <h2 class="text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                                <span class="text-blue-600">📝</span> Ficha de Membro
                            </h2>
                            <p class="text-xs text-slate-500 font-medium">Registo completo com foto e dados</p>
                        </div>
                        <span class="bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-[11px] font-black px-3 py-1 rounded-full shadow-sm">
                            Oficial IEAD
                        </span>
                    </div>

                    <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-5">
                        
                        <!-- Upload Interativo com Cores Atraentes -->
                        <div class="flex flex-col items-center justify-center p-5 bg-gradient-to-b from-blue-50/60 to-indigo-50/40 border-2 border-dashed border-indigo-200 rounded-3xl relative group hover:border-blue-500 transition duration-200">
                            <div class="relative w-24 h-24 mb-3">
                                <img id="previewFoto" src="" alt="" class="hidden w-24 h-24 rounded-full object-cover shadow-lg ring-4 ring-white border-2 border-blue-600">
                                <div id="placeholderFoto" class="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-700 text-white flex flex-col items-center justify-center shadow-lg ring-4 ring-blue-100">
                                    <svg class="w-9 h-9" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                    </svg>
                                </div>
                            </div>
                            
                            <label class="cursor-pointer bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md shadow-blue-600/30 active:scale-95 transition flex items-center gap-1.5">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                <span>Tirar Foto / Carregar</span>
                                <input type="file" name="foto" id="inputFoto" accept="image/*" capture="environment" class="hidden" onchange="mostrarPreview(event)">
                            </label>
                            <p class="text-[11px] text-slate-500 font-semibold mt-2">Fotografia do membro para a ficha</p>
                        </div>

                        <!-- 1. IDENTIFICAÇÃO -->
                        <div class="space-y-3 pt-1">
                            <span class="text-xs font-black uppercase tracking-wider text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1 rounded-lg inline-block">
                                1. Identificação Pessoal
                            </span>

                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Nome Completo *</label>
                                <input type="text" name="nome" required placeholder="Digite o nome completo" 
                                       class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white font-medium">
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Contacto Telefónico</label>
                                    <input type="text" name="telefone" placeholder="+258 84/86/87..." 
                                           class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Género</label>
                                    <select name="genero" class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white focus:border-blue-600 font-semibold">
                                        <option value="Masculino">Masculino</option>
                                        <option value="Feminino">Feminino</option>
                                    </select>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Data de Nascimento</label>
                                    <input type="date" name="data_nascimento" 
                                           class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white focus:border-blue-600 font-medium">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Segmento Etário *</label>
                                    <select name="faixa_etaria" required class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-blue-900 focus:border-blue-600">
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
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Naturalidade</label>
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" 
                                           class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Bairro / Zona</label>
                                    <select name="bairro" class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white focus:border-blue-600 font-medium">
                                        <option value="">-- Selecione a Zona --</option>
                                        {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Filiação (Pai & Mãe)</label>
                                <input type="text" name="filiacao" placeholder="Nome dos pais (especialmente para crianças)" 
                                       class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>
                        </div>

                        <!-- 2. DOCUMENTAÇÃO -->
                        <div class="space-y-3 pt-2">
                            <span class="text-xs font-black uppercase tracking-wider text-amber-900 bg-amber-50 border border-amber-200 px-3 py-1 rounded-lg inline-block">
                                2. Documentação Civil
                            </span>

                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Tipo Doc.</label>
                                    <select name="tipo_documento" class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-bold text-slate-800">
                                        <option value="BI">B.I.</option>
                                        <option value="Cédula">Cédula</option>
                                        <option value="Cartão de Eleitor">C. Eleitor</option>
                                        <option value="Passaporte">Passaporte</option>
                                        <option value="Nenhum">Sem Documento</option>
                                    </select>
                                </div>
                                <div class="sm:col-span-2">
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Número do Documento</label>
                                    <input type="text" name="numero_documento" placeholder="Número do BI ou Cédula" 
                                           class="w-full h-12 px-4 text-sm sm:text-base font-mono font-bold border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                                </div>
                            </div>
                        </div>

                        <!-- 3. VIDA ECLESIÁSTICA -->
                        <div class="space-y-3 pt-2">
                            <span class="text-xs font-black uppercase tracking-wider text-indigo-900 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-lg inline-block">
                                3. Vida Eclesiástica & Cargos
                            </span>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Ano de Conversão</label>
                                    <input type="number" name="ano_conversao" placeholder="Ex: 2016" min="1930" max="2035" 
                                           class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white font-medium">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Data Batismo Águas</label>
                                    <input type="date" name="data_batismo" 
                                           class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white focus:border-blue-600 font-medium">
                                </div>
                            </div>

                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-blue-950 mb-1.5">Posição / Cargo *</label>
                                    <select name="posicao_atual" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-blue-900 focus:border-blue-600">
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
                                    <label class="block text-sm font-bold text-indigo-950 mb-1.5">Departamento *</label>
                                    <select name="departamento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-indigo-900 focus:border-indigo-600">
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
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Espaço para Progressões Eclesiásticas</label>
                                <textarea name="progressoes" rows="2" placeholder="Ex: 2018: Obreiro, 2022: Diácono, 2025: Presbítero..." 
                                          class="w-full p-3.5 text-sm border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white"></textarea>
                            </div>

                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Observações Gerais</label>
                                <input type="text" name="observacoes" placeholder="Notas pastorais..." 
                                       class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 transition bg-slate-50/50 hover:bg-white focus:bg-white">
                            </div>
                        </div>

                        <!-- Botão de Gravação Esmeralda Vibrante -->
                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-700 hover:to-teal-800 active:scale-[0.99] text-white font-black text-base rounded-2xl shadow-xl shadow-emerald-600/30 transition duration-200 flex items-center justify-center space-x-2">
                            <span>Gravar Ficha de Membro</span>
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                        </button>
                    </form>
                </div>

                <!-- Lista de Membros com Tabela Executiva Colorida -->
                <div class="lg:col-span-7 bg-white/95 backdrop-blur-sm rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6 flex flex-col justify-between">
                    <div>
                        <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 mb-5 pb-4 border-b border-indigo-50">
                            <div>
                                <h3 class="text-lg font-black text-slate-900">Membros Registados</h3>
                                <p class="text-xs text-slate-500 font-medium">Arquivo eclesiástico digital</p>
                            </div>
                            <div>
                                <a href="/exportar/membros" class="h-11 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white rounded-xl text-xs sm:text-sm font-black shadow-md shadow-emerald-600/20 transition flex items-center justify-center gap-2 active:scale-95">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                    <span>Baixar Excel</span>
                                </a>
                            </div>
                        </div>

                        <!-- Barra de Pesquisa Rápida com Borda Azul -->
                        <div class="mb-4">
                            <div class="relative">
                                <span class="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-blue-500">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                                </span>
                                <input type="text" id="filtroMembros" onkeyup="filtrarTabela('filtroMembros', 'tabelaMembros')" 
                                       placeholder="Pesquisar por nome, BI, cargo, departamento..." 
                                       class="w-full h-12 pl-12 pr-4 text-sm sm:text-base border-2 border-indigo-100 rounded-2xl outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition bg-slate-50/50 hover:bg-white focus:bg-white font-medium">
                            </div>
                        </div>

                        <!-- Tabela Colorida com Alto Contraste -->
                        <div class="overflow-x-auto max-h-[640px] rounded-2xl border border-indigo-50">
                            <table id="tabelaMembros" class="w-full text-left text-sm min-w-[620px]">
                                <thead class="bg-gradient-to-r from-blue-900 to-indigo-950 text-white font-black text-xs uppercase tracking-wider sticky top-0 z-10">
                                    <tr>
                                        <th class="p-3.5">Membro</th>
                                        <th class="p-3.5">Posição / Cargo</th>
                                        <th class="p-3.5">Departamento</th>
                                        <th class="p-3.5">Documento</th>
                                        <th class="p-3.5 text-center">Ação</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100 text-slate-700 bg-white">
                                    {% for m in todos_membros %}
                                    <tr class="hover:bg-blue-50/60 transition">
                                        <td class="p-3.5 flex items-center space-x-3">
                                            {% if m['foto_path'] %}
                                            <img src="{{ m['foto_path'] }}" class="w-12 h-12 object-cover rounded-2xl border-2 border-white shadow-md ring-2 ring-blue-600/30">
                                            {% else %}
                                            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-700 text-white flex items-center justify-center font-black text-sm shadow-md ring-2 ring-blue-600/20">
                                                {{ m['nome'][:2].upper() }}
                                            </div>
                                            {% endif %}
                                            <div>
                                                <span class="font-extrabold text-slate-900 block text-sm sm:text-base leading-tight">{{ m['nome'] }}</span>
                                                <span class="text-xs text-slate-500 font-semibold block mt-0.5">{{ m['faixa_etaria'] or 'Adulto' }} • {{ m['telefone'] or 'Sem tel' }}</span>
                                            </div>
                                        </td>
                                        <td class="p-3.5">
                                            <span class="bg-blue-50 border border-blue-200 text-blue-900 font-black px-3 py-1 rounded-xl text-xs inline-block shadow-sm">
                                                {{ m['posicao_atual'] or 'Membro' }}
                                            </span>
                                            {% if m['progressoes'] %}
                                            <span class="text-[11px] text-indigo-700 font-bold block mt-1 truncate max-w-[150px]" title="{{ m['progressoes'] }}">📈 {{ m['progressoes'] }}</span>
                                            {% endif %}
                                        </td>
                                        <td class="p-3.5">
                                            <span class="px-3 py-1 rounded-xl text-xs font-black inline-block shadow-sm
                                                {% if m['departamento'] == 'Activista' %}bg-amber-100 text-amber-900 border border-amber-300
                                                {% elif m['departamento'] == 'Juventude' %}bg-purple-100 text-purple-900 border border-purple-300
                                                {% elif m['departamento'] == 'Mulher (Senhoras)' %}bg-rose-100 text-rose-900 border border-rose-300
                                                {% elif m['departamento'] == 'Boa Esperança (Crianças)' %}bg-emerald-100 text-emerald-900 border border-emerald-300
                                                {% else %}bg-slate-100 text-slate-800 border border-slate-300{% endif %}">
                                                {{ m['departamento'] or 'Geral' }}
                                            </span>
                                        </td>
                                        <td class="p-3.5 font-mono text-xs text-slate-700 font-bold">
                                            {{ m['tipo_documento'] or 'BI' }}: {{ m['numero_documento'] or '-' }}
                                        </td>
                                        <td class="p-3.5 text-center whitespace-nowrap">
                                            <button onclick="verCartaoMembro({{ m['id'] }})" class="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-extrabold px-3.5 py-1.5 rounded-xl text-xs shadow-md shadow-blue-600/20 transition active:scale-95 mr-1">
                                                Ficha
                                            </button>
                                            {% if e_admin %}
                                            <a href="/apagar/membro/{{ m['id'] }}" onclick="return confirm('Eliminar o membro definitivamente?');" class="text-rose-600 hover:text-rose-800 font-black text-xs p-1">
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
                <div class="lg:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50 flex items-center gap-2">
                        <span class="text-purple-600">💍</span> Registo Matrimonial
                    </h3>
                    <form action="/casamentos/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold mb-1">Nome do Noivo *</label>
                            <input type="text" name="noivo" required placeholder="Nome do noivo" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Nome da Noiva *</label>
                            <input type="text" name="noiva" required placeholder="Nome da noiva" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Data da Celebração *</label>
                            <input type="date" name="data_casamento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600 font-semibold">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Pastor Oficiante</label>
                            <input type="text" name="pastor_oficiante" placeholder="Ministro que realizou a cerimónia" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        </div>
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-purple-700 to-indigo-800 hover:from-purple-800 hover:to-indigo-900 text-white font-black rounded-2xl shadow-lg shadow-purple-900/30 transition">
                            Gravar Registo Matrimonial
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50">Livro de Casamentos</h3>
                    <div class="overflow-x-auto rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-purple-900 to-indigo-950 text-white font-black text-xs uppercase">
                                <tr><th class="p-3">Data</th><th class="p-3">Casal</th><th class="p-3">Oficiante</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for c in todos_casamentos %}
                                <tr class="hover:bg-purple-50/50 transition">
                                    <td class="p-3 font-bold">{{ c['data_casamento'] }}</td>
                                    <td class="p-3 font-extrabold text-purple-950">{{ c['noivo'] }} & {{ c['noiva'] }}</td>
                                    <td class="p-3 text-slate-600 font-medium">{{ c['pastor_oficiante'] or '-' }}</td>
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
                <div class="lg:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50 flex items-center gap-2">
                        <span class="text-slate-600">🕊️</span> Registo de Óbito
                    </h3>
                    <form action="/mortes/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold mb-1">Nome do Falecido *</label>
                            <input type="text" name="nome_falecido" required placeholder="Nome completo" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Data do Falecimento *</label>
                            <input type="date" name="data_falecimento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600 font-semibold">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Observações / Notas</label>
                            <input type="text" name="observacoes" placeholder="Dados fúnebres..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600">
                        </div>
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-slate-800 to-slate-950 text-white font-black rounded-2xl shadow-lg transition">
                            Gravar Registo de Óbito
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50">Livro de Falecimentos</h3>
                    <div class="overflow-x-auto rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-slate-800 to-slate-950 text-white font-black text-xs uppercase">
                                <tr><th class="p-3">Data</th><th class="p-3">Falecido</th><th class="p-3">Observações</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for m in todas_mortes %}
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-3 font-bold">{{ m['data_falecimento'] }}</td>
                                    <td class="p-3 font-black text-slate-900">{{ m['nome_falecido'] }}</td>
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
                <div class="bg-gradient-to-br from-amber-500 to-orange-600 text-white p-5 rounded-3xl shadow-xl shadow-amber-500/20 border border-amber-400">
                    <span class="text-xs font-black uppercase text-amber-100 block">💵 Caixa Físico</span>
                    <p class="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_caixa) }} <span class="text-xs font-bold text-amber-200">MT</span></p>
                </div>
                <div class="bg-gradient-to-br from-blue-600 to-indigo-700 text-white p-5 rounded-3xl shadow-xl shadow-blue-600/20 border border-blue-400">
                    <span class="text-xs font-black uppercase text-blue-100 block">🏛️ Conta Bancária</span>
                    <p class="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_banco) }} <span class="text-xs font-bold text-blue-200">MT</span></p>
                </div>
                <div class="bg-gradient-to-br from-emerald-600 to-teal-800 text-white p-5 rounded-3xl shadow-xl shadow-emerald-600/25 border border-emerald-400">
                    <span class="text-xs font-black uppercase text-emerald-100 block">🏦 Saldo Consolidado</span>
                    <p class="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">{{ "{:,.2f}".format(saldo_total) }} <span class="text-xs font-bold text-emerald-200">MT</span></p>
                </div>
                <div class="bg-gradient-to-br from-purple-700 to-indigo-900 text-white p-5 rounded-3xl shadow-xl shadow-purple-700/20 border border-purple-500">
                    <span class="text-xs font-black uppercase text-purple-200 block">👥 Membresia Registada</span>
                    <p class="text-2xl sm:text-3xl font-black text-white mt-2 tracking-tight">{{ total_membros }} <span class="text-xs font-bold text-purple-200">membros</span></p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-800 mb-4 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-emerald-500"></span> Entradas vs Saídas por Mês
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoEvolucaoMensal"></canvas></div>
                </div>
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-800 mb-4 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-blue-600"></span> Membros por Ministério
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoDeptos"></canvas></div>
                </div>
            </div>
        </section>

        <!-- ================= ABA TRANSFERÊNCIAS ================= -->
        <section id="aba-transferencias" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="lg:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50 flex items-center gap-2">
                        <span class="text-cyan-600">🔄</span> Transferência entre Contas
                    </h3>
                    <form action="/financeiro/transferir" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold mb-1">Data *</label>
                            <input type="date" name="data_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none font-semibold">
                        </div>
                        <div class="p-4 bg-rose-50 border-2 border-rose-200 rounded-2xl space-y-2">
                            <span class="text-xs font-black text-rose-800 uppercase block">Conta de Origem</span>
                            <select name="origem_local" class="w-full h-11 px-3 text-sm border-2 border-rose-200 rounded-xl bg-white font-bold"><option value="Caixa">💵 Caixa Físico</option><option value="Banco">🏛️ Conta Bancária</option></select>
                            <select name="origem_depto" class="w-full h-11 px-3 text-sm border-2 border-rose-200 rounded-xl bg-white"><option value="Geral">Fundo Geral</option>{% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}</select>
                        </div>
                        <div class="p-4 bg-emerald-50 border-2 border-emerald-200 rounded-2xl space-y-2">
                            <span class="text-xs font-black text-emerald-800 uppercase block">Conta de Destino</span>
                            <select name="destino_local" class="w-full h-11 px-3 text-sm border-2 border-emerald-200 rounded-xl bg-white font-bold"><option value="Banco">🏛️ Conta Bancária</option><option value="Caixa">💵 Caixa Físico</option></select>
                            <select name="destino_depto" class="w-full h-11 px-3 text-sm border-2 border-emerald-200 rounded-xl bg-white"><option value="Geral">Fundo Geral</option>{% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}</select>
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Valor da Transferência (MT) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="0.00" class="w-full h-12 px-4 text-base font-black border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Motivo *</label>
                            <input type="text" name="motivo" required placeholder="Ex: Depósito bancário, reforço..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-700 hover:from-cyan-700 hover:to-indigo-800 text-white font-black rounded-2xl shadow-lg shadow-cyan-600/25 transition duration-200">
                            Efetuar Transferência de Fundos
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50">Histórico de Transferências</h3>
                    <div class="overflow-x-auto max-h-[520px] rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-cyan-900 to-indigo-950 text-white font-black text-xs uppercase">
                                <tr><th class="p-3">Data</th><th class="p-3">De</th><th class="p-3">Para</th><th class="p-3">Motivo</th><th class="p-3 text-right">Valor</th></tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for t in ultimas_transferencias %}
                                <tr class="hover:bg-cyan-50/40 transition">
                                    <td class="p-3 font-bold">{{ t['data_movimento'] }}</td>
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
                <div class="lg:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50 flex items-center gap-2">
                        <span class="text-emerald-600">💰</span> Lançamento Financeiro
                    </h3>
                    <form action="/financeiro/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold mb-1">Data *</label>
                            <input type="date" name="data_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none font-semibold">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-sm font-bold mb-1">Tipo</label>
                                <select name="tipo" id="selectTipoTransacao" onchange="atualizarCategoriasPorTipo()" class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl bg-white font-black">
                                    <option value="Entrada">Entrada (+)</option>
                                    <option value="Saída">Saída (-)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-bold mb-1">Conta *</label>
                                <select name="local_movimento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl bg-white font-black">
                                    <option value="Caixa">💵 Caixa</option>
                                    <option value="Banco">🏛️ Banco</option>
                                </select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-sm font-bold mb-1">Fundo / Depto</label>
                                <select name="departamento" class="w-full h-12 px-3 text-sm border-2 border-slate-200 rounded-2xl bg-white font-semibold">
                                    <option value="Geral">Geral</option>
                                    {% for d in lista_deptos %}<option value="{{ d['nome'] }}">{{ d['nome'] }}</option>{% endfor %}
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-bold mb-1">Categoria</label>
                                <select name="categoria" id="selectCategoriaTransacao" class="w-full h-12 px-3 text-sm border-2 border-slate-200 rounded-2xl bg-white font-semibold"></select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Valor (MT) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="0.00" class="w-full h-12 px-4 text-base font-black border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Descrição</label>
                            <input type="text" name="descricao" required placeholder="Detalhes do movimento" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white font-black rounded-2xl shadow-xl shadow-emerald-600/30 transition">
                            Gravar Lançamento no Caixa
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 pb-3 border-b border-indigo-50">
                        <h3 class="text-base sm:text-lg font-black text-slate-900">Extrato de Movimentos</h3>
                        <a href="/exportar/financeiro" class="h-10 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white rounded-xl text-xs font-black shadow-md shadow-emerald-600/20 transition flex items-center gap-1.5">
                            <span>📥 Exportar Excel</span>
                        </a>
                    </div>
                    <div class="overflow-x-auto max-h-[520px] rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-emerald-900 to-teal-950 text-white font-black text-xs uppercase sticky top-0">
                                <tr><th class="p-3">Data</th><th class="p-3">Tipo</th><th class="p-3">Conta</th><th class="p-3">Categoria</th><th class="p-3">Descrição</th><th class="p-3 text-right">Valor</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for f in todas_financas %}
                                <tr class="hover:bg-emerald-50/40 transition">
                                    <td class="p-3 font-bold">{{ f['data_movimento'] }}</td>
                                    <td class="p-3"><span class="px-2.5 py-1 rounded-full text-xs font-black {{ 'bg-emerald-100 text-emerald-800 border border-emerald-300' if f['tipo'] == 'Entrada' else 'bg-rose-100 text-rose-800 border border-rose-300' }}">{{ f['tipo'] }}</span></td>
                                    <td class="p-3 font-extrabold text-slate-800">{{ f['local_movimento'] }}</td>
                                    <td class="p-3 font-semibold text-slate-700">{{ f['categoria'] }}</td>
                                    <td class="p-3 text-slate-500 text-xs">{{ f['descricao'] }}</td>
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
                <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
                    <h3 class="text-sm font-black uppercase text-blue-950 mb-3 pb-2 border-b flex items-center gap-1.5">
                        <span class="text-blue-600">🏛️</span> Ministérios / Deptos
                    </h3>
                    <form action="/config/departamento/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Novo departamento" required class="h-11 px-3 text-sm border-2 border-slate-200 rounded-xl w-full outline-none">
                        <button type="submit" class="bg-blue-900 text-white px-4 font-black rounded-xl hover:bg-blue-950">+</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for d in lista_deptos %}<li class="py-2.5 flex justify-between font-semibold"><span>{{ d['nome'] }}</span><a href="/config/departamento/apagar/{{ d['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
                    <h3 class="text-sm font-black uppercase text-emerald-950 mb-3 pb-2 border-b flex items-center gap-1.5">
                        <span class="text-emerald-600">🏷️</span> Categorias Financeiras
                    </h3>
                    <form action="/config/categoria/novo" method="POST" class="space-y-2 mb-3 text-sm">
                        <div class="flex gap-2">
                            <select name="tipo" class="h-11 px-2 border-2 border-slate-200 rounded-xl bg-white w-1/3 text-xs font-black"><option value="Entrada">Entrada</option><option value="Saída">Saída</option></select>
                            <input type="text" name="nome" placeholder="Nome" required class="h-11 px-3 border-2 border-slate-200 rounded-xl w-2/3 outline-none">
                        </div>
                        <button type="submit" class="w-full h-10 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl">+ Guardar Categoria</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for c in lista_categorias %}<li class="py-2.5 flex justify-between font-semibold"><span><strong class="text-emerald-700">{{ c['tipo'] }}</strong>: {{ c['nome'] }}</span><a href="/config/categoria/apagar/{{ c['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
                    <h3 class="text-sm font-black uppercase text-amber-950 mb-3 pb-2 border-b flex items-center gap-1.5">
                        <span class="text-amber-600">📍</span> Zonas & Bairros
                    </h3>
                    <form action="/config/zona/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Nova zona..." required class="h-11 px-3 text-sm border-2 border-slate-200 rounded-xl w-full outline-none">
                        <button type="submit" class="bg-amber-600 text-white px-4 font-black rounded-xl hover:bg-amber-700">+</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for z in lista_zonas %}<li class="py-2.5 flex justify-between font-semibold"><span>{{ z['nome'] }}</span><a href="/config/zona/apagar/{{ z['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
            </div>
        </section>

        <!-- ================= ABA UTILIZADORES ================= -->
        <section id="aba-usuarios" class="tab-content space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                <div class="md:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50 flex items-center gap-2">
                        <span class="text-emerald-600">👤</span> Criar Acesso ao Sistema
                    </h3>
                    <form action="/usuarios/novo" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold mb-1">Nome de Utilizador *</label>
                            <input type="text" name="usuario" required placeholder="Ex: secretaria ou tesoureiro" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 font-medium">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Palavra-passe *</label>
                            <input type="password" name="senha" required placeholder="••••••••" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-1">Nível de Acesso (Cargo) *</label>
                            <select name="cargo" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl bg-white font-black text-blue-950">
                                <option value="Secretário">Secretário (Apenas Cadastro de Membros e Eventos)</option>
                                <option value="Líder">Líder de Ministério (Apenas Cadastro)</option>
                                <option value="Tesoureiro">Tesoureiro (Apenas Tesouraria e Dashboard)</option>
                                <option value="Pastor">Pastor (Administrador Geral)</option>
                            </select>
                        </div>
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white font-black rounded-2xl shadow-lg shadow-emerald-600/30 transition">
                            Criar Utilizador
                        </button>
                    </form>
                </div>
                <div class="md:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50">Utilizadores Registados</h3>
                    <div class="overflow-x-auto rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-blue-900 to-indigo-950 text-white font-black text-xs uppercase">
                                <tr><th class="p-3">Login</th><th class="p-3">Cargo / Permissão</th><th class="p-3 text-center">Ação</th></tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for u in lista_usuarios %}
                                <tr>
                                    <td class="p-3 font-extrabold text-slate-900">{{ u['usuario'] }}</td>
                                    <td class="p-3">
                                        <span class="px-3 py-1 rounded-xl text-xs font-black inline-block shadow-sm
                                            {% if 'Pastor' in u['cargo'] %}bg-blue-100 text-blue-900 border border-blue-300
                                            {% elif 'Tesoureiro' in u['cargo'] %}bg-emerald-100 text-emerald-900 border border-emerald-300
                                            {% else %}bg-amber-100 text-amber-900 border border-amber-300{% endif %}">
                                            {{ u['cargo'] }}
                                        </span>
                                    </td>
                                    <td class="p-3 text-center">
                                        {% if u['usuario'] != 'admin' %}<a href="/usuarios/apagar/{{ u['id'] }}" onclick="return confirm('Eliminar utilizador?');" class="text-rose-600 font-bold">✕</a>
                                        {% else %}<span class="text-slate-400 text-xs font-black">Principal</span>{% endif %}
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

    <!-- Modal Cartão de Membro Estilo Nobre -->
    <div id="modalMembro" class="fixed inset-0 bg-slate-950/70 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl relative border border-slate-200">
            <button onclick="fecharModalMembro()" class="absolute top-5 right-5 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold text-base flex items-center justify-center transition">&times;</button>
            <div id="conteudoModalMembro" class="space-y-4"></div>
        </div>
    </div>

    <script>
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
                ? `<img src="${m.foto_path}" class="w-28 h-28 object-cover rounded-3xl mx-auto border-4 border-white shadow-xl ring-4 ring-blue-600/30">`
                : `<div class="w-28 h-28 rounded-3xl bg-gradient-to-tr from-blue-600 to-indigo-700 text-white flex items-center justify-center text-3xl font-black mx-auto border-4 border-white shadow-xl ring-4 ring-blue-600/30">${m.nome.substring(0,2).toUpperCase()}</div>`;

            document.getElementById('conteudoModalMembro').innerHTML = `
                <div class="text-center pb-4 border-b border-indigo-50">
                    ${fotoHtml}
                    <h3 class="text-xl font-black text-slate-900 mt-3">${m.nome}</h3>
                    <div class="flex justify-center gap-2 mt-2 flex-wrap">
                        <span class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white text-xs font-black px-3.5 py-1 rounded-full shadow-sm">${m.posicao_atual || 'Membro'}</span>
                        <span class="bg-indigo-50 text-indigo-900 border border-indigo-200 text-xs font-black px-3.5 py-1 rounded-full">${m.departamento || 'Geral'}</span>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3 text-sm text-slate-700 bg-slate-50 p-4 rounded-2xl border border-slate-200/80 font-medium">
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Segmento</span><strong>${m.faixa_etaria || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Contacto</span><strong>${m.telefone || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Documento</span><strong>${m.tipo_documento || 'BI'}: ${m.numero_documento || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Naturalidade</span><strong>${m.naturalidade || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Bairro / Zona</span><strong>${m.bairro || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Ano Conversão</span><strong>${m.ano_conversao || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Data Batismo</span><strong>${m.data_batismo || '-'}</strong></div>
                    <div><span class="text-xs text-slate-400 font-bold block uppercase">Filiação</span><strong>${m.filiacao || '-'}</strong></div>
                </div>
                <div class="p-4 bg-blue-50/70 rounded-2xl border border-blue-200">
                    <span class="text-xs font-black text-blue-950 uppercase tracking-wider block mb-1">Histórico de Progressões Eclesiásticas</span>
                    <p class="text-slate-800 text-xs font-semibold whitespace-pre-line leading-relaxed">${m.progressoes || 'Nenhuma alteração de cargo registada até ao momento.'}</p>
                </div>
                <button onclick="window.print()" class="w-full h-12 bg-gradient-to-r from-slate-900 to-indigo-950 text-white font-black text-sm rounded-2xl shadow-md transition flex items-center justify-center gap-2">
                    <span>🖨️ Imprimir Cartão de Membro</span>
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
                btn.className = 'tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 text-indigo-100 hover:bg-white/10 hover:text-white';
            });
            const abaAlvo = document.getElementById('aba-' + abaId);
            if (abaAlvo) abaAlvo.classList.add('active');
            const activeBtn = document.getElementById('btn-' + abaId);
            if (activeBtn) activeBtn.className = 'tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-black shadow-md shadow-blue-900/40';
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
                    { label: 'Entradas', data: {{ evolucao_entradas | safe }}, borderColor: '#059669', backgroundColor: 'rgba(5, 150, 105, 0.1)', borderWidth: 3, tension: 0.35, fill: true },
                    { label: 'Saídas', data: {{ evolucao_saidas | safe }}, borderColor: '#e11d48', backgroundColor: 'rgba(225, 29, 72, 0.05)', borderWidth: 3, tension: 0.35, fill: true }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        new Chart(document.getElementById('graficoDeptos').getContext('2d'), {
            type: 'bar',
            data: {
                labels: {{ depto_labels | safe }},
                datasets: [{ label: 'Membros', data: {{ depto_valores | safe }}, backgroundColor: ['#2563eb', '#7c3aed', '#db2777', '#059669', '#d97706', '#0284c7'], borderRadius: 10 }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
        {% endif %}
    </script>
</body>
</html>
"""

with open(os.path.join("templates", "dashboard.html"), "w", encoding="utf-8") as f:
    f.write(html_colorido)

print("✓ Novo design vibrante e colorido gerado em templates/dashboard.html!")