with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

bloco_import = """import os
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None
"""

# Substituir o início das importações para garantir que psycopg2 é sempre importado com try/except
if "import psycopg2" in code:
    print("psycopg2 já se encontra no código.")
else:
    code = bloco_import + "\n" + code
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Importação protegida de psycopg2 adicionada ao topo do app.py!")