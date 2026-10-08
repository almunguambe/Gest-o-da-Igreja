import os

print("A analisar o sistema...")

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Verifica se o motor foi apagado
if "app = Flask(" not in code:
    print("Motor apagado detetado. A restaurar...")
    
    cabecalho_vital = """import os
import json
import sqlite3
from datetime import datetime
import io
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash

# A CHAVE DE IGNIÇÃO DO SISTEMA
app = Flask(__name__)
app.secret_key = "iead_chicuque_chave_super_segura_2026"
app.config['UPLOAD_FOLDER'] = os.path.join("static", "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

"""
    # Limpa aquele "import qrcode" solto e injeta o cabeçalho correto no topo
    code = code.replace("import qrcode\n", "")
    code = cabecalho_vital + code
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Motor Flask restaurado com sucesso!")
else:
    print("O motor já está no ficheiro. Tudo OK.")