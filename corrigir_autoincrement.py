with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir AUTOINCREMENT no próprio texto do app.py caso existam comandos fixos
code = code.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
code = code.replace("integer primary key autoincrement", "serial primary key")
code = code.replace("AUTOINCREMENT", "")

# Garantir que a classe HybridCursor intercepte e limpe AUTOINCREMENT em tempo de execução
trecho_antigo_cur = "def execute(self, sql, params=None):"
trecho_novo_cur = """def execute(self, sql, params=None):
        if 'AUTOINCREMENT' in sql.upper():
            import re
            sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
            sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)"""

if trecho_antigo_cur in code and "flags=re.IGNORECASE" not in code:
    code = code.replace(trecho_antigo_cur, trecho_novo_cur, 1)
    print("✓ Tradução automática de AUTOINCREMENT adicionada ao cursor!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.py saneado contra AUTOINCREMENT!")