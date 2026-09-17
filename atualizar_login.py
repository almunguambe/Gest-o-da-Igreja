import os

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

novo_login_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEAD Chicuque - Portal Administrativo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .bg-pattern {
            background-color: #060e23;
            background-image: radial-gradient(at 10% 20%, rgba(30, 58, 138, 0.4) 0px, transparent 50%),
                              radial-gradient(at 90% 80%, rgba(37, 99, 235, 0.25) 0px, transparent 50%),
                              radial-gradient(at 50% 50%, rgba(15, 23, 42, 0.8) 0px, transparent 100%);
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
    </style>
</head>
<body class="bg-pattern min-h-screen flex items-center justify-center p-4 selection:bg-blue-600 selection:text-white relative overflow-hidden">

    <!-- Efeitos Decorativos de Luz -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none"></div>

    <div class="w-full max-w-md z-10 space-y-4">
        
        <!-- Cartão Principal de Login -->
        <div class="glass-card rounded-3xl shadow-2xl border border-white/40 p-8 sm:p-10 transition-all duration-300 hover:shadow-blue-900/20">
            
            <!-- Logótipo e Cabeçalho -->
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-24 h-24 mb-4 rounded-2xl bg-gradient-to-tr from-blue-950 via-blue-900 to-indigo-800 p-2 shadow-xl ring-4 ring-blue-50 relative group">
                    <!-- Imagem oficial da Logo -->
                    <img src="/static/logo.png" alt="Logo IEAD" class="w-full h-full object-contain rounded-xl" onerror="this.style.display='none'; document.getElementById('emblema-padrao').style.display='flex';">
                    
                    <!-- Emblema de recurso (SVG da Bíblia e Cruz) caso logo.png não exista ainda -->
                    <div id="emblema-padrao" style="display:none;" class="w-full h-full items-center justify-center text-amber-300">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                    </div>
                </div>

                <span class="inline-block text-[11px] font-bold uppercase tracking-widest text-blue-800 bg-blue-50 px-3 py-1 rounded-full border border-blue-100 mb-2">
                    Assembleia de Deus
                </span>
                <h1 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-tight">
                    Congregação de Chicuque
                </h1>
                <p class="text-xs font-medium text-slate-500 mt-1">
                    Sistema de Gestão & Tesouraria Eclesiástica
                </p>
            </div>

            <!-- Alerta de Erro -->
            {% if erro %}
            <div class="mb-5 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-semibold flex items-center space-x-2 animate-shake">
                <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span>{{ erro }}</span>
            </div>
            {% endif %}

            <!-- Formulário de Autenticação -->
            <form action="/login" method="POST" class="space-y-4">
                
                <div>
                    <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5 ml-1">Utilizador</label>
                    <div class="relative">
                        <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </span>
                        <input type="text" name="usuario" required placeholder="ex: admin ou tesoureiro" 
                               class="w-full pl-10 pr-4 py-3 bg-slate-50 hover:bg-slate-100/80 focus:bg-white border border-slate-200 focus:border-blue-600 rounded-xl outline-none text-xs sm:text-sm font-medium transition duration-200 focus:ring-4 focus:ring-blue-600/10">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold uppercase text-slate-700 mb-1.5 ml-1">Palavra-passe</label>
                    <div class="relative">
                        <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </span>
                        <input type="password" name="senha" required placeholder="••••••••" 
                               class="w-full pl-10 pr-4 py-3 bg-slate-50 hover:bg-slate-100/80 focus:bg-white border border-slate-200 focus:border-blue-600 rounded-xl outline-none text-xs sm:text-sm font-medium transition duration-200 focus:ring-4 focus:ring-blue-600/10">
                    </div>
                </div>

                <button type="submit" 
                        class="w-full bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 hover:from-blue-950 hover:to-indigo-950 text-white text-xs sm:text-sm font-bold py-3.5 rounded-xl shadow-lg shadow-blue-900/30 active:scale-[0.99] transition duration-200 flex items-center justify-center space-x-2 mt-2">
                    <span>Aceder ao Portal</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                </button>
            </form>
        </div>

        <!-- Rodapé do Login -->
        <div class="text-center text-slate-400 text-[11px] space-y-1">
            <p class="font-medium text-slate-300">"Tudo quanto fizerdes, fazei-o de todo o coração, como ao Senhor."</p>
            <p class="text-slate-500 font-semibold">Colossenses 3:23 • IEAD Chicuque</p>
        </div>

    </div>

</body>
</html>
"""

with open(os.path.join("templates", "login.html"), "w", encoding="utf-8") as f:
    f.write(novo_login_html)

print("✓ Novo ecrã de login elegante gerado em templates/login.html!")