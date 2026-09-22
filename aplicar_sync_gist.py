with open("app.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Bloco com cabeçalho de navegador para garantir download 100% livre de bloqueios
codigo_sync = '''
GIST_URL = "https://gist.githubusercontent.com/almunguambe/b9f7af1814fb7674e3a0dbeded9389b7/raw/usuarios.json"

def sync_puxar_nuvem():
    """Restaura automaticamente todos os utilizadores e alunos do Gist para o SQLite local"""
    try:
        req = urllib.request.Request(
            GIST_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
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

# 1. Garantir que urllib.request está no topo
if "import urllib.request" not in conteudo:
    conteudo = "import urllib.request\n" + conteudo

# 2. Substituir ou injetar as funções de sync
if "def sync_puxar_nuvem():" in conteudo:
    linhas = conteudo.splitlines()
    novas = []
    pulando = False
    for l in linhas:
        if "GIST_URL =" in l or "BLOB_URL =" in l or "JSONBIN_KEY =" in l or "def sync_puxar_nuvem():" in l:
            pulando = True
        elif pulando and l.startswith("def init_db():"):
            pulando = False
            novas.append(codigo_sync)
            novas.append(l)
        elif not pulando:
            novas.append(l)
    conteudo = "\n".join(novas)
else:
    conteudo = conteudo.replace("def init_db():", codigo_sync + "\ndef init_db():")

# 3. Garantir chamada ao final de init_db
if "sync_puxar_nuvem()" not in conteudo:
    conteudo = conteudo.replace("init_db()\n", "init_db()\ntry:\n    sync_puxar_nuvem()\nexcept:\n    pass\n")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✓ app.py configurado com o GitHub Gist com sucesso!")