with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

rota_reset = """
# =======================================================
# ROTA TEMPORÁRIA: REDEFINIR SENHA ADMIN NA NUVEM
# =======================================================
@app.route('/redefinir_senha_urgente_admin_2026')
def redefinir_senha_urgente_admin():
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = bool(DATABASE_URL and psycopg2)
        param = "%s" if is_pg else "?"
        
        # Redefine a senha do admin para: admin123
        cur.execute(f"UPDATE usuarios SET senha = {param} WHERE usuario = {param}", ('admin123', 'admin'))
        conn.commit()
        if hasattr(conn, 'close'):
            conn.close()
            
        return '''
        <div style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
            <h1 style="color: #15803d;">✓ Senha Redefinida com Sucesso no Render!</h1>
            <p style="font-size: 18px;">Utilizador: <b>admin</b></p>
            <p style="font-size: 18px;">Nova Palavra-passe: <b style="background: #fef08a; padding: 4px 8px; border-radius: 4px;">admin123</b></p>
            <br><br>
            <a href="/login" style="background: #0d3b66; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">Ir para o Login</a>
        </div>
        '''
    except Exception as e:
        return f"<h3>Erro ao redefinir: {e}</h3>"
"""

if '/redefinir_senha_urgente_admin_2026' not in conteudo:
    conteudo += "\n" + rota_reset
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ Rota temporária adicionada ao app.py com sucesso!")
else:
    print("A rota já se encontra no app.py.")