with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

idx_censo = code.find("@app.route('/censo'")
if idx_censo != -1:
    idx_cols = code.find("cols_db = [r[0].lower()", idx_censo)
    if idx_cols != -1:
        print("--- TRECHO DO INSERT / COMMIT ---")
        print(code[idx_cols:idx_cols+1200])
    else:
        print("Trecho cols_db não localizado.")
else:
    print("Rota censo não localizada.")