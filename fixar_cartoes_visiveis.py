import os

dash_path = os.path.join("templates", "dashboard.html")

novo_dashboard = """<!DOCTYPE html>
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

    <!-- Topbar -->
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

            <div class="flex items-center space-x-2.5">
                <div class="hidden sm:flex flex-col text-right pr-1">
                    <span class="text-xs font-black text-white leading-none tracking-wide">{{ session['usuario'] }}</span>
                    <span class="text-[11px] text-amber-300 font-bold mt-0.5">{{ session['cargo'] }}</span>
                </div>
                <div class="sm:hidden px-2.5 py-1 bg-indigo-900/80 rounded-xl border border-indigo-400/30 text-[11px] font-bold text-amber-300">
                    {{ session['usuario'] }}
                </div>
                <a href="/logout" class="bg-gradient-to-r from-rose-500 to-red-600 hover:from-rose-600 hover:to-red-700 active:scale-95 text-white text-xs font-extrabold px-3.5 py-2 rounded-xl shadow-md transition duration-150">
                    Sair
                </a>
            </div>
        </div>

        <!-- Abas -->
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
                <a href="/financeiro/balancete_pdf" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 bg-emerald-600/90 text-white hover:bg-emerald-600 font-extrabold shadow-sm">
                    <span>📑</span> <span>Balancete Oficial (PDF)</span>
                </a>
                <a href="/sistema/backup" class="tab-btn px-4 py-2.5 rounded-2xl transition flex items-center gap-2 bg-amber-600/90 text-white hover:bg-amber-600 font-extrabold shadow-sm">
                    <span>💾</span> <span>Backup (.ZIP)</span>
                </a>
                {% endif %}
            </nav>
        </div>
    </header>

    <main class="max-w-7xl mx-auto p-3.5 sm:p-5 lg:p-6 space-y-6">

        {% if alerta_duplicado %}
        <div class="p-4 bg-amber-50 border-2 border-amber-300 rounded-2xl flex items-center gap-3 text-amber-900 font-bold text-sm shadow-md">
            <span class="text-2xl">⚠️</span>
            <span>{{ alerta_duplicado }}</span>
        </div>
        {% endif %}

        {% if sucesso_cadastro %}
        <div class="p-4 bg-emerald-50 border-2 border-emerald-300 rounded-2xl flex items-center gap-3 text-emerald-900 font-bold text-sm shadow-md">
            <span class="text-2xl">✅</span>
            <span>{{ sucesso_cadastro }}</span>
        </div>
        {% endif %}

        {% if pode_cadastro %}
        <!-- ================= ABA MEMBROS ================= -->
        <section id="aba-membros" class="tab-content {% if pode_cadastro %}active{% endif %} space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                <!-- Formulário de Registo -->
                <div class="lg:col-span-5 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <div class="flex items-center justify-between pb-4 mb-5 border-b border-indigo-50">
                        <div>
                            <h2 class="text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                                <span class="text-blue-600">📝</span> Ficha de Membro
                            </h2>
                            <p class="text-xs text-slate-500 font-medium">Registo com fotografia e documentos</p>
                        </div>
                        <span class="bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-[11px] font-black px-3 py-1 rounded-full shadow-sm">Oficial IEAD</span>
                    </div>

                    <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-5">
                        <div class="flex flex-col items-center justify-center p-5 bg-gradient-to-b from-blue-50/60 to-indigo-50/40 border-2 border-dashed border-indigo-200 rounded-3xl relative group hover:border-blue-500 transition duration-200">
                            <div class="relative w-24 h-24 mb-3">
                                <img id="previewFoto" src="" alt="" class="hidden w-24 h-24 rounded-full object-cover shadow-lg ring-4 ring-white border-2 border-blue-600">
                                <div id="placeholderFoto" class="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-700 text-white flex flex-col items-center justify-center shadow-lg ring-4 ring-blue-100">
                                    <svg class="w-9 h-9" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                </div>
                            </div>
                            <label class="cursor-pointer bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md shadow-blue-600/30 active:scale-95 transition flex items-center gap-1.5">
                                <span>Tirar Foto / Carregar</span>
                                <input type="file" name="foto" id="inputFoto" accept="image/*" capture="environment" class="hidden" onchange="mostrarPreview(event)">
                            </label>
                            <p class="text-[11px] text-slate-500 font-semibold mt-2">Fotografia do membro para a ficha</p>
                        </div>

                        <div class="space-y-3 pt-1">
                            <span class="text-xs font-black uppercase tracking-wider text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1 rounded-lg inline-block">1. Identificação Pessoal</span>
                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Nome Completo *</label>
                                <input type="text" name="nome" required placeholder="Digite o nome completo" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600 font-medium">
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Contacto Telefónico</label>
                                    <input type="text" name="telefone" placeholder="+258 8..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-blue-600">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Género</label>
                                    <select name="genero" class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-semibold">
                                        <option value="Masculino">Masculino</option>
                                        <option value="Feminino">Feminino</option>
                                    </select>
                                </div>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Data de Nascimento</label>
                                    <input type="date" name="data_nascimento" class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Segmento Etário *</label>
                                    <select name="faixa_etaria" required class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-blue-900">
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
                                    <input type="text" name="naturalidade" placeholder="Cidade / Província" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Bairro / Zona</label>
                                    <select name="bairro" class="w-full h-12 px-3.5 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white">
                                        <option value="">-- Selecione a Zona --</option>
                                        {% for z in lista_zonas %}<option value="{{ z['nome'] }}">{{ z['nome'] }}</option>{% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Filiação (Pai & Mãe)</label>
                                <input type="text" name="filiacao" placeholder="Nome dos pais" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                            </div>
                        </div>

                        <div class="space-y-3 pt-2">
                            <span class="text-xs font-black uppercase tracking-wider text-amber-900 bg-amber-50 border border-amber-200 px-3 py-1 rounded-lg inline-block">2. Documentação Civil</span>
                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Tipo Doc.</label>
                                    <select name="tipo_documento" class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-bold">
                                        <option value="BI">B.I.</option>
                                        <option value="Cédula">Cédula</option>
                                        <option value="Cartão de Eleitor">C. Eleitor</option>
                                        <option value="Passaporte">Passaporte</option>
                                        <option value="Nenhum">Sem Documento</option>
                                    </select>
                                </div>
                                <div class="sm:col-span-2">
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Número do Documento</label>
                                    <input type="text" name="numero_documento" placeholder="Número do BI ou Cédula" class="w-full h-12 px-4 text-sm sm:text-base font-mono font-bold border-2 border-slate-200 rounded-2xl outline-none">
                                </div>
                            </div>
                        </div>

                        <div class="space-y-3 pt-2">
                            <span class="text-xs font-black uppercase tracking-wider text-indigo-900 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-lg inline-block">3. Vida Eclesiástica & Cargos</span>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Ano de Conversão</label>
                                    <input type="number" name="ano_conversao" placeholder="Ex: 2016" min="1930" max="2035" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none font-medium">
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-800 mb-1.5">Data Batismo Águas</label>
                                    <input type="date" name="data_batismo" class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none font-medium">
                                </div>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-sm font-bold text-blue-950 mb-1.5">Posição / Cargo *</label>
                                    <select name="posicao_atual" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-blue-900">
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
                                    <select name="departamento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none bg-white font-black text-indigo-900">
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
                                <textarea name="progressoes" rows="2" placeholder="Histórico ministerial..." class="w-full p-3.5 text-sm border-2 border-slate-200 rounded-2xl outline-none"></textarea>
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-slate-800 mb-1.5">Observações Gerais</label>
                                <input type="text" name="observacoes" placeholder="Notas pastorais..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                            </div>
                        </div>

                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-700 hover:to-teal-800 active:scale-[0.99] text-white font-black text-base rounded-2xl shadow-xl transition duration-200 flex items-center justify-center space-x-2">
                            <span>Gravar Ficha de Membro</span>
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                        </button>
                    </form>
                </div>

                <!-- Lista de Membros com CARTOES INDIVIDUAIS VISÍVEIS -->
                <div class="lg:col-span-7 space-y-4">
                    
                    <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
                        <div>
                            <h3 class="text-lg font-black text-slate-900">Membros Registados ({{ total_membros }})</h3>
                            <p class="text-xs text-slate-500 font-medium">Toque nos botões de cada membro para emitir documentos</p>
                        </div>
                        <a href="/exportar/membros" class="h-11 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white rounded-xl text-xs sm:text-sm font-black shadow-md transition flex items-center justify-center gap-2 active:scale-95">
                            <span>📥 Baixar Excel</span>
                        </a>
                    </div>

                    <!-- Pesquisa Rápida -->
                    <input type="text" id="filtroMembrosCards" onkeyup="filtrarCardsMembros()" 
                           placeholder="🔍 Pesquisar membro por nome, cargo ou departamento..." 
                           class="w-full h-12 px-4 text-sm border-2 border-indigo-100 rounded-2xl outline-none focus:border-blue-600 transition bg-white shadow-sm font-medium">

                    <!-- LISTA DE CARTOES INDIVIDUAIS - 100% VISÍVEL EM QUALQUER ECRÃ -->
                    <div id="listaCardsMembros" class="space-y-4 max-h-[750px] overflow-y-auto pr-1">
                        {% if not todos_membros %}
                        <div class="bg-white p-8 rounded-3xl text-center border-2 border-dashed border-slate-200 text-slate-400">
                            <span class="text-3xl block mb-2">👤</span>
                            <p class="font-bold">Ainda não há membros registados.</p>
                            <p class="text-xs mt-1">Preencha o formulário ao lado para cadastrar o primeiro membro.</p>
                        </div>
                        {% endif %}

                        {% for m in todos_membros %}
                        <div class="card-membro-item bg-white/95 rounded-3xl p-5 border border-indigo-100 shadow-md space-y-4 transition hover:shadow-lg">
                            
                            <!-- Cabeçalho do Membro -->
                            <div class="flex items-start justify-between gap-3 pb-3 border-b border-slate-100">
                                <div class="flex items-center space-x-3.5">
                                    {% if m['foto_path'] %}
                                    <img src="{{ m['foto_path'] }}" class="w-14 h-14 object-cover rounded-2xl border-2 border-blue-600 shadow-md flex-shrink-0">
                                    {% else %}
                                    <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-700 text-white flex items-center justify-center font-black text-base shadow-md flex-shrink-0">
                                        {{ m['nome'][:2].upper() }}
                                    </div>
                                    {% endif %}
                                    <div>
                                        <h4 class="font-extrabold text-base text-slate-900 leading-tight">{{ m['nome'] }}</h4>
                                        <div class="flex items-center gap-1.5 mt-1 flex-wrap">
                                            <span class="bg-blue-50 border border-blue-200 text-blue-900 font-black px-2.5 py-0.5 rounded-lg text-xs">{{ m['posicao_atual'] or 'Membro' }}</span>
                                            <span class="bg-slate-100 border text-slate-700 font-bold px-2 py-0.5 rounded-lg text-xs">{{ m['departamento'] or 'Geral' }}</span>
                                            <span class="text-xs text-slate-400 font-semibold">• {{ m['faixa_etaria'] or 'Adulto' }}</span>
                                        </div>
                                    </div>
                                </div>

                                {% if e_admin %}
                                <a href="/apagar/membro/{{ m['id'] }}" onclick="return confirm('Eliminar o membro definitivamente?');" title="Eliminar" class="w-8 h-8 rounded-full bg-rose-50 hover:bg-rose-100 text-rose-600 font-black text-xs flex items-center justify-center transition flex-shrink-0">
                                    ✕
                                </a>
                                {% endif %}
                            </div>

                            <!-- Dados Rápidos -->
                            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-600 bg-slate-50/80 p-3 rounded-2xl border border-slate-100 font-medium">
                                <div><span class="text-slate-400 block text-[10px] uppercase font-bold">Documento</span><strong>{{ m['tipo_documento'] or 'BI' }}: {{ m['numero_documento'] or '-' }}</strong></div>
                                <div><span class="text-slate-400 block text-[10px] uppercase font-bold">Contacto</span><strong>{{ m['telefone'] or 'Sem telefone' }}</strong></div>
                                <div><span class="text-slate-400 block text-[10px] uppercase font-bold">Batismo / Conv.</span><strong>Bat: {{ m['data_batismo'] or '-' }}</strong></div>
                            </div>

                            <!-- BOTÕES DE AÇÃO DESTACADOS E COLORIDOS -->
                            <div class="space-y-2 pt-1">
                                <!-- Botão Azul: Cartão PDF & Botão Verde: WhatsApp -->
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    <!-- BOTÃO AZUL: BAIXAR CARTÃO OFICIAL EM PDF -->
                                    <a href="/membro/cartao_pdf/{{ m['id'] }}" class="h-11 bg-gradient-to-r from-blue-700 to-indigo-800 hover:from-blue-800 hover:to-indigo-900 active:scale-95 text-white font-black text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition">
                                        <span>🪪</span> <span>Baixar Cartão (PDF)</span>
                                    </a>

                                    <!-- BOTÃO VERDE: CONVERSAR NO WHATSAPP -->
                                    {% if m['telefone'] %}
                                    <a href="https://wa.me/258{{ m['telefone']|replace(' ', '')|replace('+', '')|replace('-', '') }}" target="_blank" class="h-11 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 active:scale-95 text-white font-black text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition">
                                        <span>💬</span> <span>Falar no WhatsApp</span>
                                    </a>
                                    {% else %}
                                    <button disabled class="h-11 bg-slate-100 text-slate-400 font-bold text-xs rounded-xl flex items-center justify-center gap-2 cursor-not-allowed">
                                        <span>💬</span> <span>Sem Contacto</span>
                                    </button>
                                    {% endif %}
                                </div>

                                <!-- 3 BOTÕES BRANCOS: CERTIFICADOS EM PDF -->
                                <div class="p-2.5 bg-indigo-50/50 border border-indigo-100 rounded-2xl">
                                    <span class="text-[11px] font-black text-indigo-950 uppercase tracking-wider block mb-1.5">📜 Emitir Certificado Oficial em PDF:</span>
                                    <div class="grid grid-cols-3 gap-1.5">
                                        <a href="/membro/certificado_pdf/{{ m['id'] }}/batismo" class="py-2 bg-white hover:bg-blue-50 border border-blue-200 text-blue-900 font-extrabold text-center text-xs rounded-xl shadow-sm transition active:scale-95">
                                            Batismo
                                        </a>
                                        <a href="/membro/certificado_pdf/{{ m['id'] }}/apresentacao" class="py-2 bg-white hover:bg-emerald-50 border border-emerald-200 text-emerald-900 font-extrabold text-center text-xs rounded-xl shadow-sm transition active:scale-95">
                                            Apresentação
                                        </a>
                                        <a href="/membro/certificado_pdf/{{ m['id'] }}/recomendacao" class="py-2 bg-white hover:bg-purple-50 border border-purple-200 text-purple-900 font-extrabold text-center text-xs rounded-xl shadow-sm transition active:scale-95">
                                            Recomendação
                                        </a>
                                    </div>
                                </div>
                            </div>

                        </div>
                        {% endfor %}
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
                        <input type="text" name="noivo" required placeholder="Nome do noivo *" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        <input type="text" name="noiva" required placeholder="Nome da noiva *" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        <input type="date" name="data_casamento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600 font-semibold">
                        <input type="text" name="pastor_oficiante" placeholder="Pastor Oficiante" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-purple-600">
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-purple-700 to-indigo-800 text-white font-black rounded-2xl shadow-lg transition">Gravar Matrimónio</button>
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
                                    <td class="p-3 text-slate-600">{{ c['pastor_oficiante'] or '-' }}</td>
                                    {% if e_admin %}<td class="p-3 text-center"><a href="/apagar/casamento/{{ c['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a></td>{% endif %}
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
                        <input type="text" name="nome_falecido" required placeholder="Nome do Falecido *" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600">
                        <input type="date" name="data_falecimento" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600 font-semibold">
                        <input type="text" name="observacoes" placeholder="Observações..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none focus:border-slate-600">
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-slate-800 to-slate-950 text-white font-black rounded-2xl shadow-lg transition">Gravar Óbito</button>
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
                                <tr>
                                    <td class="p-3 font-bold">{{ m['data_falecimento'] }}</td>
                                    <td class="p-3 font-black text-slate-900">{{ m['nome_falecido'] }}</td>
                                    <td class="p-3 text-slate-500">{{ m['observacoes'] or '-' }}</td>
                                    {% if e_admin %}<td class="p-3 text-center"><a href="/apagar/morte/{{ m['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a></td>{% endif %}
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
                        <span class="w-3 h-3 rounded-full bg-emerald-500"></span> Evolução Mensal (Entradas vs Saídas)
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoEvolucaoMensal"></canvas></div>
                </div>
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-800 mb-4 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-blue-600"></span> Situação por Departamento (Fundos)
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoFinancasDepto"></canvas></div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-800 mb-4 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-teal-500"></span> Fontes de Fundos (Entradas)
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoFontesFundos"></canvas></div>
                </div>
                <div class="bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-800 mb-4 flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-rose-500"></span> Destino de Saídas (Despesas)
                    </h3>
                    <div class="h-64 sm:h-72"><canvas id="graficoSaidasCategorias"></canvas></div>
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
                            <input type="text" name="motivo" required placeholder="Justificação..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-700 text-white font-black rounded-2xl shadow-lg transition duration-200">
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
                            <input type="text" name="descricao" required placeholder="Detalhes..." class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        </div>
                        <button type="submit" class="w-full h-14 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white font-black rounded-2xl shadow-xl transition">
                            Gravar Lançamento no Caixa
                        </button>
                    </form>
                </div>
                <div class="lg:col-span-7 bg-white/95 rounded-3xl card-glow border border-indigo-100 p-5 sm:p-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 pb-3 border-b border-indigo-50">
                        <h3 class="text-base sm:text-lg font-black text-slate-900">Extrato de Movimentos</h3>
                        <a href="/exportar/financeiro" class="h-10 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl text-xs font-black shadow-md transition flex items-center gap-1.5">
                            <span>📥 Exportar Excel</span>
                        </a>
                    </div>
                    <div class="overflow-x-auto max-h-[520px] rounded-2xl border border-indigo-50">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gradient-to-r from-emerald-900 to-teal-950 text-white font-black text-xs uppercase sticky top-0">
                                <tr><th class="p-3">Data</th><th class="p-3">Tipo</th><th class="p-3">Conta</th><th class="p-3">Categoria</th><th class="p-3 text-right">Valor</th><th class="p-3 text-center">Recibo</th>{% if e_admin %}<th class="p-3 text-center">Ação</th>{% endif %}</tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 bg-white">
                                {% for f in todas_financas %}
                                <tr class="hover:bg-emerald-50/40 transition">
                                    <td class="p-3 font-bold">{{ f['data_movimento'] }}</td>
                                    <td class="p-3"><span class="px-2.5 py-1 rounded-full text-xs font-black {{ 'bg-emerald-100 text-emerald-800 border border-emerald-300' if f['tipo'] == 'Entrada' else 'bg-rose-100 text-rose-800 border border-rose-300' }}">{{ f['tipo'] }}</span></td>
                                    <td class="p-3 font-extrabold text-slate-800">{{ f['local_movimento'] }}</td>
                                    <td class="p-3 font-semibold text-slate-700">{{ f['categoria'] }}</td>
                                    <td class="p-3 text-right font-black {{ 'text-emerald-700' if f['tipo'] == 'Entrada' else 'text-rose-700' }}">{{ "{:,.2f}".format(f['valor']) }} MT</td>
                                    <td class="p-3 text-center">
                                        <a href="/financeiro/recibo_pdf/{{ f['id'] }}" class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-2.5 py-1 rounded text-xs inline-block">📄 Recibo (PDF)</a>
                                    </td>
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
                    <h3 class="text-sm font-black uppercase text-blue-950 mb-3 pb-2 border-b">Ministérios / Deptos</h3>
                    <form action="/config/departamento/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Novo departamento" required class="h-11 px-3 text-sm border-2 border-slate-200 rounded-xl w-full">
                        <button type="submit" class="bg-blue-900 text-white px-4 font-black rounded-xl">+</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for d in lista_deptos %}<li class="py-2.5 flex justify-between font-semibold"><span>{{ d['nome'] }}</span><a href="/config/departamento/apagar/{{ d['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
                    <h3 class="text-sm font-black uppercase text-emerald-950 mb-3 pb-2 border-b">Categorias Financeiras</h3>
                    <form action="/config/categoria/novo" method="POST" class="space-y-2 mb-3 text-sm">
                        <div class="flex gap-2">
                            <select name="tipo" class="h-11 px-2 border-2 border-slate-200 rounded-xl bg-white w-1/3 text-xs font-black"><option value="Entrada">Entrada</option><option value="Saída">Saída</option></select>
                            <input type="text" name="nome" placeholder="Nome" required class="h-11 px-3 border-2 border-slate-200 rounded-xl w-2/3">
                        </div>
                        <button type="submit" class="w-full h-10 bg-emerald-600 text-white font-black rounded-xl">+ Guardar</button>
                    </form>
                    <ul class="divide-y divide-slate-100 text-sm max-h-56 overflow-y-auto">
                        {% for c in lista_categorias %}<li class="py-2.5 flex justify-between font-semibold"><span><strong class="text-emerald-700">{{ c['tipo'] }}</strong>: {{ c['nome'] }}</span><a href="/config/categoria/apagar/{{ c['id'] }}" class="text-rose-600 font-bold">✕</a></li>{% endfor %}
                    </ul>
                </div>
                <div class="bg-white/95 p-5 rounded-3xl card-glow border border-indigo-100">
                    <h3 class="text-sm font-black uppercase text-amber-950 mb-3 pb-2 border-b">Zonas & Bairros</h3>
                    <form action="/config/zona/novo" method="POST" class="flex gap-2 mb-3">
                        <input type="text" name="nome" placeholder="Nova zona..." required class="h-11 px-3 text-sm border-2 border-slate-200 rounded-xl w-full">
                        <button type="submit" class="bg-amber-600 text-white px-4 font-black rounded-xl">+</button>
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
                    <h3 class="text-base sm:text-lg font-black text-slate-900 mb-4 pb-3 border-b border-indigo-50">👤 Criar Acesso</h3>
                    <form action="/usuarios/novo" method="POST" class="space-y-4">
                        <input type="text" name="usuario" required placeholder="Utilizador *" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        <input type="password" name="senha" required placeholder="Palavra-passe *" class="w-full h-12 px-4 text-sm sm:text-base border-2 border-slate-200 rounded-2xl outline-none">
                        <select name="cargo" required class="w-full h-12 px-3 text-sm sm:text-base border-2 border-slate-200 rounded-2xl bg-white font-black text-blue-950">
                            <option value="Secretário">Secretário (Apenas Cadastro de Membros e Eventos)</option>
                            <option value="Líder">Líder de Ministério (Apenas Cadastro)</option>
                            <option value="Tesoureiro">Tesoureiro (Apenas Tesouraria e Dashboard)</option>
                            <option value="Pastor">Pastor (Administrador Geral)</option>
                        </select>
                        <button type="submit" class="w-full h-12 bg-gradient-to-r from-emerald-600 to-teal-700 text-white font-black rounded-2xl shadow-lg transition">Criar Utilizador</button>
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
                                    <td class="p-3"><span class="px-3 py-1 rounded-xl text-xs font-black inline-block bg-blue-100 text-blue-900">{{ u['cargo'] }}</span></td>
                                    <td class="p-3 text-center">{% if u['usuario'] != 'admin' %}<a href="/usuarios/apagar/{{ u['id'] }}" onclick="return confirm('Eliminar?');" class="text-rose-600 font-bold">✕</a>{% else %}<span class="text-slate-400 text-xs font-black">Principal</span>{% endif %}</td>
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

        function filtrarCardsMembros() {
            const filtro = document.getElementById('filtroMembrosCards').value.toLowerCase();
            const cards = document.getElementsByClassName('card-membro-item');
            for (let i = 0; i < cards.length; i++) {
                cards[i].style.display = cards[i].innerText.toLowerCase().includes(filtro) ? '' : 'none';
            }
        }

        {% if pode_tesouraria %}
        const paletaCores = ['#059669', '#2563eb', '#d97706', '#7c3aed', '#db2777', '#0891b2', '#ea580c', '#4f46e5'];
        const paletaSaidas = ['#e11d48', '#f97316', '#dc2626', '#9333ea', '#c026d3', '#b91c1c', '#64748b'];

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

        new Chart(document.getElementById('graficoFinancasDepto').getContext('2d'), {
            type: 'bar',
            data: {
                labels: {{ depto_fin_labels | safe }},
                datasets: [
                    { label: 'Entradas', data: {{ depto_fin_entradas | safe }}, backgroundColor: '#059669', borderRadius: 6 },
                    { label: 'Saídas', data: {{ depto_fin_saidas | safe }}, backgroundColor: '#e11d48', borderRadius: 6 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        new Chart(document.getElementById('graficoFontesFundos').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: {{ fontes_labels | safe }},
                datasets: [{
                    data: {{ fontes_valores | safe }},
                    backgroundColor: paletaCores,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11, weight: 'bold' } } } }
            }
        });

        new Chart(document.getElementById('graficoSaidasCategorias').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: {{ saidas_labels | safe }},
                datasets: [{
                    data: {{ saidas_valores | safe }},
                    backgroundColor: paletaSaidas,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11, weight: 'bold' } } } }
            }
        });
        {% endif %}
    </script>
</body>
</html>
"""

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(novo_dashboard)

print("✓ templates/dashboard.html atualizado com cartões individuais 100% visíveis!")