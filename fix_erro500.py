with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Garantir que as novas colunas existem fisicamente no PostgreSQL/SQLite
script_migracao = '''
def migrar_banco_imediato():
    try:
        conn = get_db_connection() if 'get_db_connection' in globals() else get_db()
        c = conn.cursor() if hasattr(conn, 'cursor') else conn
        colunas = [
            ("zona", "VARCHAR(150)"),
            ("celula", "VARCHAR(150)"),
            ("bairro", "VARCHAR(150)"),
            ("distrito", "VARCHAR(150)"),
            ("estado", "VARCHAR(50) DEFAULT 'Activo'")
        ]
        for col, tipo in colunas:
            try:
                c.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
                conn.commit()
            except Exception:
                if hasattr(conn, 'rollback'): conn.rollback()
        conn.close()
    except Exception as err:
        print(f"Aviso migracao: {err}")

try:
    migrar_banco_imediato()
except Exception:
    pass
'''

if "def migrar_banco_imediato():" not in conteudo:
    if "if __name__ ==" in conteudo:
        conteudo = conteudo.replace("if __name__ ==", script_migracao + "\nif __name__ ==")
    else:
        conteudo += "\n" + script_migracao

# 2. Assegurar que 'todos_membros' é passado no render_template do dashboard
if "return render_template('dashboard.html'," in conteudo:
    # Se todos_membros não estiver na chamada, adicioná-lo
    if "todos_membros=todos_membros" not in conteudo and "todos_membros=" not in conteudo:
        conteudo = conteudo.replace(
            "return render_template('dashboard.html',",
            "return render_template('dashboard.html',\n                           todos_membros=todos_membros,"
        )

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py atualizado com migração segura e variável todos_membros!")