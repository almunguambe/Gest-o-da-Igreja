with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substitui o padrão de count que tenta ler indice [0] diretamente em dicionários
padrao_antigo = '.fetchone()[0]'
# Função de leitura segura: se for dict pega o primeiro valor, se for tupla pega o índice 0
helper_seguro = """
def _val(row):
    if row is None:
        return 0
    if isinstance(row, dict):
        return list(row.values())[0]
    return row[0]
"""

if "_val(row)" not in code:
    # Insere logo no início após os imports
    idx_import = code.find("app = Flask")
    if idx_import != -1:
        code = code[:idx_import] + helper_seguro.strip() + "\n\n" + code[idx_import:]
        print("✓ Helper _val adicionado!")

# Substitui ocorrências críticas no dashboard
trecho_total = 'total_membros = conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (igreja_id,)).fetchone()[0]'
trecho_total_novo = 'total_membros = _val(conn.execute("SELECT COUNT(*) FROM membros WHERE igreja_id = ?", (igreja_id,)).fetchone())'

if trecho_total in code:
    code = code.replace(trecho_total, trecho_total_novo)
    print("✓ Linha do total_membros adaptada com _val()!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)