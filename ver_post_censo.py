with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

idx_censo = code.find("@app.route('/censo'")
if idx_censo != -1:
    idx_homologar = code.find("@app.route('/admin/censo/homologar'", idx_censo)
    trecho = code[idx_censo:idx_homologar] if idx_homologar != -1 else code[idx_censo:idx_censo+4000]
    
    # Procurar onde está o POST e o INSERT
    idx_post = trecho.find("request.method == 'POST'")
    if idx_post != -1:
        print("--- BLOCO POST DO CENSO ---")
        print(trecho[idx_post:idx_post+2500])
    else:
        print("Trecho de POST não encontrado explicitamente. Imprimindo trecho geral:")
        print(trecho[800:3000])
else:
    print("Rota /censo não encontrada.")