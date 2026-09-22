with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

novo_bloco = '''GIST_URL = "https://gist.githubusercontent.com/almunguambe/b9f7af1814fb7674e3a0dbeded9389b7/raw/33e08b96f9f953b0b9d7f277f6c6f2548d037db8/usuarios.json"

def sync_puxar_nuvem():
    """Restaura automaticamente todos os utilizadores e alunos do Gist para o SQLite local"""
    import urllib.request
    import json
    import ssl
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            GIST_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=25) as response:
            usuarios = json.loads(response.read().decode("utf-8"))
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            for u in usuarios:
                c.execute("INSERT OR REPLACE INTO usuarios (usuario, senha, cargo) VALUES (?, ?, ?)",
                          (u["usuario"], u["senha"], u["cargo"]))
            conn.commit()
            conn.close()
            print(f"✓ {len(usuarios)} utilizadores sincronizados com sucesso do Gist!")
    except Exception as e:
        print(f"Aviso sync Gist: {e}")
'''

linhas = conteudo.splitlines()
novas = []
pulando = False
substituido = False

for l in linhas:
    if "GIST_URL =" in l or "def sync_puxar_nuvem():" in l:
        if not substituido:
            novas.append(novo_bloco)
            substituido = True
        pulando = True
    elif pulando and l.startswith("def init_db():"):
        pulando = False
        novas.append(l)
    elif not pulando:
        novas.append(l)

with open("app.py", "w", encoding="utf-8") as f:
    f.write("\n".join(novas))

print("✓ app.py atualizado com sucesso!")