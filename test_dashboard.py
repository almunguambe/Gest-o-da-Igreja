import app

# 1. Ativar modo debug local para ver o erro completo se houver
app.app.config['DEBUG'] = True
app.app.config['TESTING'] = True

client = app.app.test_client()

print("--- TESTE 1: Acessar '/' seguindo redirecionamentos ---")
res = client.get('/', follow_redirects=True)
print("Status final:", res.status_code)
print("URL final acessada:", res.request.path if hasattr(res, 'request') else 'N/A')

print("\n--- TESTE 2: Executar dashboard diretamente como funcao ---")
with app.app.test_request_context('/'):
    # Injetar todas as chaves possiveis de sessao
    from flask import session
    session['logged_in'] = True
    session['usuario'] = 'admin'
    session['user'] = 'admin'
    session['username'] = 'admin'
    session['funcao'] = 'Admin'
    session['role'] = 'admin'
    session['tipo'] = 'Admin'
    
    try:
        resultado = app.dashboard()
        print("✓ Rota dashboard() executou com sucesso localmente!")
    except Exception as e:
        import traceback
        print("! ERRO DETECTADO DENTRO DE DASHBOARD:")
        traceback.print_exc()