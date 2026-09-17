import os

# 1. Garante que as pastas essenciais existem
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# 2. requirements.txt (informa ao Render o que instalar)
requirements_txt = """flask
gunicorn
openpyxl
"""
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements_txt)
print("✓ requirements.txt criado com sucesso!")

# 3. Procfile (informa ao Render como arrancar o serviço)
with open("Procfile", "w", encoding="utf-8") as f:
    f.write("web: gunicorn app:app\n")
print("✓ Procfile criado com sucesso!")

# 4. templates/login.html
login_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entrar - Assembleia de Deus Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 flex items-center justify-center min-h-screen p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
        <div class="text-center mb-6">
            <img src="/static/logo.png" alt="Logo" class="w-20 h-20 mx-auto object-contain mb-3" onerror="this.style.display='none'">
            <h1 class="text-base font-bold text-slate-800 uppercase">Igreja Evangélica Assembleia de Deus</h1>
            <p class="text-xs font-semibold text-blue-800 uppercase mt-1">Chicuque • Acesso Restrito</p>
        </div>
        {% if erro %}
        <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg font-medium text-center">
            {{ erro }}
        </div>
        {% endif %}
        <form action="/login" method="POST" class="space-y-4 text-xs">
            <div>
                <label class="block font-bold text-slate-700 uppercase mb-1">Utilizador</label>
                <input type="text" name="usuario" required placeholder="admin" class="w-full p-2.5 border rounded-lg outline-none focus:ring-2 focus:ring-blue-600">
            </div>
            <div>
                <label class="block font-bold text-slate-700 uppercase mb-1">Palavra-passe</label>
                <input type="password" name="senha" required placeholder="••••••••" class="w-full p-2.5 border rounded-lg outline-none focus:ring-2 focus:ring-blue-600">
            </div>
            <button type="submit" class="w-full bg-blue-800 hover:bg-blue-900 text-white font-bold py-2.5 rounded-lg transition">Iniciar Sessão</button>
        </form>
    </div>
</body>
</html>
"""
with open(os.path.join("templates", "login.html"), "w", encoding="utf-8") as f:
    f.write(login_html)
print("✓ templates/login.html criado com sucesso!")