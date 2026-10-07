with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

termo = "/censo"
pos = 0
encontrados = 0

while True:
    idx = code.find(termo, pos)
    if idx == -1:
        break
    # Procurar o início da rota mais próxima
    inicio = code.rfind('@app.route', 0, idx)
    if inicio != -1:
        print(f"--- ROTA ENCONTRADA (pos {inicio}) ---")
        print(code[inicio:inicio+1500])
        print("="*60)
        encontrados += 1
    pos = idx + len(termo)

if encontrados == 0:
    print("Nenhuma rota com /censo encontrada.")