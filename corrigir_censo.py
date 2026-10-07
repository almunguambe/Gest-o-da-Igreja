# Script de auto-reparo das rotas do censo
with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Garante que time e psycopg2 estão disponíveis
cabecalho_imports = """
import time
import os
try:
    import psycopg2
except ImportError:
    psycopg2 = None
"""

if "import time" not in conteudo:
    conteudo = cabecalho_imports + "\n" + conteudo

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Importações verificadas e corrigidas no app.py!")