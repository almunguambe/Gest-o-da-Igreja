import os
import sys

# Definir a nova palavra-passe pretendida
NOVA_SENHA = "admin"  # Pode alterar para qualquer outra palavra-passe aqui

try:
    import app
except ImportError:
    print("❌ Erro: O ficheiro app.py não foi encontrado nesta pasta.")
    sys.exit(1)

def redefinir_senha_admin():
    conn = None
    try:
        conn = app.get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        
        is_postgres = bool(getattr(app, 'DATABASE_URL', None) and getattr(app, 'psycopg2', None))
        param = "%s" if is_postgres else "?"
        
        # 1. Verificar se o utilizador admin existe
        cur.execute(f"SELECT id, usuario, cargo FROM usuarios WHERE usuario = {param}", ('admin',))
        admin_user = cur.fetchone()
        
        if admin_user:
            # 2. Atualizar a palavra-passe existente
            cur.execute(f"UPDATE usuarios SET senha = {param} WHERE usuario = {param}", (NOVA_SENHA, 'admin'))
            conn.commit()
            print("==================================================")
            print("✓ Palavra-passe do utilizador 'admin' redefinida com sucesso!")
            print(f"👉 Utilizador: admin")
            print(f"👉 Nova Senha: {NOVA_SENHA}")
            print("==================================================")
        else:
            # 3. Caso não exista, cria o utilizador admin principal
            cur.execute(
                f"INSERT INTO usuarios (usuario, senha, cargo) VALUES ({param}, {param}, {param})",
                ('admin', NOVA_SENHA, 'Pastor')
            )
            conn.commit()
            print("==================================================")
            print("✓ Utilizador 'admin' não existia e foi criado com sucesso!")
            print(f"👉 Utilizador: admin")
            print(f"👉 Nova Senha: {NOVA_SENHA}")
            print("👉 Permissão : Pastor (Administrador Geral)")
            print("==================================================")

    except Exception as e:
        print(f"❌ Erro ao redefinir a palavra-passe: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == '__main__':
    redefinir_senha_admin()