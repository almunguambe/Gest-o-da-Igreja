import re

# 1. ATUALIZAR O APP.PY COM AS ROTAS DE RECUPERAÇÃO
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

rotas_recuperacao = """
# =======================================================
# MÓDULO DE RECUPERAÇÃO DE PALAVRA-PASSE (ADMIN)
# =======================================================
import random
import time

# Armazena temporariamente códigos de verificação em memória
# Formato: {'email': {'codigo': '123456', 'expira': timestamp}}
CODIGOS_RECUPERACAO = {}
EMAIL_ADMIN_AUTORIZADO = "almunguame@gmail.com"

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    msg_erro = None
    msg_sucesso = None
    
    if request.method == 'POST':
        email_digitado = (request.form.get('email') or '').strip().lower()
        
        if email_digitado == EMAIL_ADMIN_AUTORIZADO.lower():
            # Gera código aleatório de 6 dígitos
            codigo = f"{random.randint(100000, 999999)}"
            CODIGOS_RECUPERACAO[email_digitado] = {
                'codigo': codigo,
                'expira': time.time() + 900  # 15 minutos
            }
            session['email_reset'] = email_digitado
            # Redireciona para a tela de confirmação
            return redirect('/confirmar-codigo-recuperacao')
        else:
            msg_erro = "E-mail não reconhecido como administrador autorizado do sistema."
            
    return render_template('esqueci_senha.html', msg_erro=msg_erro)


@app.route('/confirmar-codigo-recuperacao', methods=['GET', 'POST'])
def confirmar_codigo_recuperacao():
    email = session.get('email_reset')
    if not email or email not in CODIGOS_RECUPERACAO:
        return redirect('/esqueci-senha')
        
    dados_codigo = CODIGOS_RECUPERACAO[email]
    codigo_ativo = dados_codigo['codigo']
    msg_erro = None
    
    if request.method == 'POST':
        codigo_informado = (request.form.get('codigo') or '').strip()
        nova_senha = (request.form.get('nova_senha') or '').strip()
        confirmar_senha = (request.form.get('confirmar_senha') or '').strip()
        
        if time.time() > dados_codigo['expira']:
            msg_erro = "O código expirou. Solicite um novo código."
        elif codigo_informado != codigo_ativo:
            msg_erro = "Código de confirmação incorreto. Verifique atentamente."
        elif len(nova_senha) < 4:
            msg_erro = "A nova palavra-passe deve conter pelo menos 4 caracteres."
        elif nova_senha != confirmar_senha:
            msg_erro = "As palavras-passe digitadas não coincidem."
        else:
            # Atualiza no Banco de Dados
            try:
                conn = get_db()
                cur = conn.cursor() if hasattr(conn, 'cursor') else conn
                param = "%s" if bool(DATABASE_URL and psycopg2) else "?"
                cur.execute(f"UPDATE usuarios SET senha = {param} WHERE usuario = {param}", (nova_senha, 'admin'))
                conn.commit()
                if hasattr(conn, 'close'):
                    conn.close()
                del CODIGOS_RECUPERACAO[email]
                session.pop('email_reset', None)
                session['sucesso_login_msg'] = "Palavra-passe do administrador redefinida com sucesso!"
                return redirect('/login')
            except Exception as e:
                msg_erro = f"Erro ao atualizar na base de dados: {e}"

    return render_template('confirmar_codigo.html', email=email, codigo_dica=codigo_ativo, msg_erro=msg_erro)
"""

if '/esqueci-senha' not in code:
    code += "\n" + rotas_recuperacao
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rotas de recuperação integradas em app.py!")
else:
    print("As rotas de recuperação já constam em app.py.")

# 2. CRIAR O TEMPLATE templates/esqueci_senha.html
html_esqueci = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperação de Acesso - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl border border-slate-100">
        <div class="text-center mb-6">
            <span class="text-4xl">🔐</span>
            <h1 class="text-xl font-black text-slate-900 mt-2">Recuperar Acesso do Administrador</h1>
            <p class="text-xs text-slate-500 mt-1">Insira o e-mail de segurança autorizado para prosseguir</p>
        </div>

        {% if msg_erro %}
        <div class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-bold text-center">
            {{ msg_erro }}
        </div>
        {% endif %}

        <form action="/esqueci-senha" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1">E-mail Cadastrado:</label>
                <input type="email" name="email" required placeholder="almunguame@gmail.com" class="w-full h-12 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none font-semibold">
            </div>

            <button type="submit" class="w-full h-12 bg-blue-900 hover:bg-blue-950 text-white font-black text-sm rounded-xl shadow-lg transition">
                Confirmar E-mail & Gerar Código
            </button>
        </form>

        <div class="mt-6 text-center border-t pt-4">
            <a href="/login" class="text-xs font-bold text-slate-500 hover:text-slate-800">← Voltar ao Login</a>
        </div>
    </div>
</body>
</html>
"""
with open('templates/esqueci_senha.html', 'w', encoding='utf-8') as f:
    f.write(html_esqueci)
print("✓ Template templates/esqueci_senha.html criado!")

# 3. CRIAR O TEMPLATE templates/confirmar_codigo.html
html_confirmar = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validar Código de Segurança - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl border border-slate-100">
        <div class="text-center mb-6">
            <span class="text-4xl">🔑</span>
            <h1 class="text-xl font-black text-slate-900 mt-2">Validação de Segurança</h1>
            <p class="text-xs text-slate-500 mt-1">E-mail validado: <b>{{ email }}</b></p>
        </div>

        <div class="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-center">
            <span class="text-[11px] font-bold text-amber-900 uppercase tracking-wider block">Código de Confirmação Oficial:</span>
            <span class="text-2xl font-black tracking-widest text-blue-950 font-mono">{{ codigo_dica }}</span>
            <p class="text-[10px] text-amber-700 mt-1">Válido por 15 minutos</p>
        </div>

        {% if msg_erro %}
        <div class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-bold text-center">
            {{ msg_erro }}
        </div>
        {% endif %}

        <form action="/confirmar-codigo-recuperacao" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1">Código de 6 Dígitos:</label>
                <input type="text" name="codigo" required maxlength="6" placeholder="Insira o código" class="w-full h-11 px-3 text-center text-lg font-mono tracking-widest border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none font-bold">
            </div>

            <div>
                <label class="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1">Nova Palavra-passe:</label>
                <input type="password" name="nova_senha" required placeholder="Nova palavra-passe" class="w-full h-11 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
            </div>

            <div>
                <label class="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1">Confirmar Nova Palavra-passe:</label>
                <input type="password" name="confirmar_senha" required placeholder="Repita a palavra-passe" class="w-full h-11 px-3 text-sm border-2 rounded-xl border-slate-200 focus:border-blue-600 focus:outline-none">
            </div>

            <button type="submit" class="w-full h-12 bg-emerald-700 hover:bg-emerald-800 text-white font-black text-sm rounded-xl shadow-lg transition">
                Gravar Nova Palavra-passe
            </button>
        </form>

        <div class="mt-6 text-center border-t pt-4">
            <a href="/esqueci-senha" class="text-xs font-bold text-slate-500 hover:text-slate-800">← Reenviar outro código</a>
        </div>
    </div>
</body>
</html>
"""
with open('templates/confirmar_codigo.html', 'w', encoding='utf-8') as f:
    f.write(html_confirmar)
print("✓ Template templates/confirmar_codigo.html criado!")

# 4. ADICIONAR LINK NO ECRÃ DE LOGIN (templates/login.html se existir)
try:
    with open('templates/login.html', 'r', encoding='utf-8') as f:
        login_html = f.read()
    
    if '/esqueci-senha' not in login_html:
        if '</form>' in login_html:
            link_rec = '<div class="text-center mt-3"><a href="/esqueci-senha" class="text-xs text-blue-900 font-bold hover:underline">Esqueci a palavra-passe?</a></div></form>'
            login_html = login_html.replace('</form>', link_rec, 1)
            with open('templates/login.html', 'w', encoding='utf-8') as f:
                f.write(login_html)
            print("✓ Link 'Esqueci a palavra-passe' inserido no templates/login.html!")
except Exception as e:
    print("Nota sobre login.html:", e)