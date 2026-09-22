with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

codigo_sync = '''
JSONBIN_KEY = "$2a$10$AnLf2hbmM0bjeYIxshoFV.U4TadUmDhFugTGzO7FvcuqgkFxbijPO"
JSONBIN_ID = "6aaecc9bac6210605ae07985"

def sync_puxar_nuvem():
    """Restaura automaticamente utilizadores e alunos da nuvem para o SQLite local"""
    try:
        req = urllib.request.Request(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}/latest",
            headers={"X-Master-Key": JSONBIN_KEY}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            usuarios = data.get("record", [])
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            for u in usuarios:
                c.execute("INSERT OR REPLACE INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                          (u["usuario"], u["senha"], u["cargo"]))
            conn.commit()
            conn.close()
            print(f"✓ {len(usuarios)} utilizadores restaurados da nuvem!")
    except Exception as e:
        print(f"Aviso sync puxar: {e}")

def sync_enviar_nuvem():
    """Envia a lista de utilizadores e alunos locais para a nuvem"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT usuario, senha, cargo FROM usuarios")
        rows = c.fetchall()
        lista = [{"usuario": r["usuario"], "senha": r["senha"], "cargo": r["cargo"]} for r in rows]
        conn.close()

        req = urllib.request.Request(
            f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}",
            data=json.dumps(lista).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Master-Key": JSONBIN_KEY
            },
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print("✓ Nuvem atualizada com os novos utilizadores!")
    except Exception as e:
        print(f"Aviso sync enviar: {e}")
'''

# 1. Garantir que urllib.request está importado
if "import urllib.request" not in conteudo:
    conteudo = "import urllib.request\n" + conteudo

# 2. Inserir as funções antes de def init_db()
if "def sync_puxar_nuvem():" not in conteudo:
    conteudo = conteudo.replace("def init_db():", codigo_sync + "\ndef init_db():")

# 3. Invocar a recuperação no final de init_db()
if "sync_puxar_nuvem()" not in conteudo:
    conteudo = conteudo.replace("init_db()\n", "init_db()\ntry:\n    sync_puxar_nuvem()\nexcept:\n    pass\n")

# 4. Acionar o envio automático ao adicionar ou remover utilizadores
if "sync_enviar_nuvem()" not in conteudo:
    conteudo = conteudo.replace(
        "flash('Usuário adicionado com sucesso!', 'success')",
        "try:\n                sync_enviar_nuvem()\n            except:\n                pass\n            flash('Usuário adicionado com sucesso!', 'success')"
    )
    conteudo = conteudo.replace(
        "flash('Usuário removido com sucesso!', 'success')",
        "try:\n        sync_enviar_nuvem()\n    except:\n        pass\n        flash('Usuário removido com sucesso!', 'success')"
    )

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ Sincronização automática com o ID 6aaecc9bac6210605ae07985 integrada!")