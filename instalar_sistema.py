import os

# 1. Garante que a pasta 'templates' existe
os.makedirs("templates", exist_ok=True)

# 2. Escreve automaticamente o ficheiro index.html
html_conteudo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal de Gestão da Igreja</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800 font-sans">

    <header class="bg-indigo-900 text-white p-4 sticky top-0 shadow-md z-10">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-xl font-bold tracking-wide">⛪ Gestão Eclesiástica</h1>
            <span class="text-xs bg-indigo-700 px-3 py-1 rounded-full text-indigo-200">Online</span>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 space-y-6">

        <!-- Métricas Rápidas -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                <span class="text-xs font-semibold text-gray-500 uppercase">Membros</span>
                <p class="text-2xl font-bold text-gray-800 mt-1">{{ total_membros }}</p>
            </div>
            <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                <span class="text-xs font-semibold text-emerald-600 uppercase">Entradas</span>
                <p class="text-xl font-bold text-emerald-600 mt-1">{{ "{:,.2f}".format(entradas) }} MT</p>
            </div>
            <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                <span class="text-xs font-semibold text-rose-500 uppercase">Saídas</span>
                <p class="text-xl font-bold text-rose-500 mt-1">{{ "{:,.2f}".format(saidas) }} MT</p>
            </div>
            <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                <span class="text-xs font-semibold text-indigo-600 uppercase">Saldo em Caixa</span>
                <p class="text-xl font-bold text-indigo-700 mt-1">{{ "{:,.2f}".format(saldo) }} MT</p>
            </div>
        </div>

        <!-- Formulários -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- Registar Membro -->
            <div class="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
                <h2 class="text-lg font-bold text-gray-800 mb-3">👤 Registar Novo Membro</h2>
                <form action="/membro/adicionar" method="POST" class="space-y-3">
                    <input type="text" name="nome" placeholder="Nome Completo" required 
                           class="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-indigo-400 outline-none text-sm">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <input type="text" name="telefone" placeholder="Contacto / Telemóvel" 
                               class="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-indigo-400 outline-none text-sm">
                        <input type="text" name="departamento" placeholder="Ministério / Célula" 
                               class="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-indigo-400 outline-none text-sm">
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg text-sm transition">
                        Guardar Membro
                    </button>
                </form>
            </div>

            <!-- Lançamento Financeiro -->
            <div class="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
                <h2 class="text-lg font-bold text-gray-800 mb-3">💰 Lançamento (Dízimos / Despesas)</h2>
                <form action="/transacao/adicionar" method="POST" class="space-y-3">
                    <div class="grid grid-cols-2 gap-2">
                        <select name="tipo" class="w-full p-2.5 border rounded-lg text-sm bg-white outline-none">
                            <option value="Entrada">Entrada (+)</option>
                            <option value="Saída">Saída (-)</option>
                        </select>
                        <select name="categoria" class="w-full p-2.5 border rounded-lg text-sm bg-white outline-none">
                            <option value="Dízimo">Dízimo</option>
                            <option value="Oferta">Oferta</option>
                            <option value="Doação">Doação</option>
                            <option value="Manutenção">Manutenção</option>
                            <option value="Ação Social">Ação Social</option>
                            <option value="Outros">Outros</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <input type="number" step="0.01" name="valor" placeholder="Valor (MT)" required 
                               class="w-full p-2.5 border rounded-lg text-sm outline-none">
                        <select name="membro_id" class="w-full p-2.5 border rounded-lg text-sm bg-white outline-none">
                            <option value="">-- Membro Opcional --</option>
                            {% for m in todos_membros %}
                            <option value="{{ m['id'] }}">{{ m['nome'] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <input type="text" name="descricao" placeholder="Descrição ou Observações" 
                           class="w-full p-2.5 border rounded-lg text-sm outline-none">
                    <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-lg text-sm transition">
                        Confirmar Transação
                    </button>
                </form>
            </div>

        </div>

        <!-- Tabela -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <h2 class="text-base font-bold text-gray-800 mb-3">Últimas Transações Registadas</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead class="bg-gray-50 text-gray-500 border-b">
                        <tr>
                            <th class="p-2">Data</th>
                            <th class="p-2">Tipo</th>
                            <th class="p-2">Categoria</th>
                            <th class="p-2">Membro</th>
                            <th class="p-2 text-right">Valor</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        {% for t in transacoes %}
                        <tr>
                            <td class="p-2 text-gray-500 whitespace-nowrap">{{ t['data'] }}</td>
                            <td class="p-2">
                                <span class="px-2 py-0.5 rounded text-xs font-semibold {{ 'bg-emerald-100 text-emerald-700' if t['tipo'] == 'Entrada' else 'bg-rose-100 text-rose-700' }}">
                                    {{ t['tipo'] }}
                                </span>
                            </td>
                            <td class="p-2 font-medium">{{ t['categoria'] }}</td>
                            <td class="p-2 text-gray-600">{{ t['membro_nome'] if t['membro_nome'] else '-' }}</td>
                            <td class="p-2 text-right font-bold {{ 'text-emerald-600' if t['tipo'] == 'Entrada' else 'text-rose-600' }}">
                                {{ "{:,.2f}".format(t['valor']) }} MT
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

    </main>
</body>
</html>
"""

# Salva o arquivo HTML dentro da pasta templates
with open(os.path.join("templates", "index.html"), "w", encoding="utf-8") as f:
    f.write(html_conteudo)

print("✓ Ficheiro 'templates/index.html' criado com sucesso!")

# 3. Escreve automaticamente o ficheiro app.py
app_conteudo = """from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "gestao_igreja.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            departamento TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Entrada', 'Saída')),
            categoria TEXT,
            valor REAL,
            data TEXT,
            membro_id INTEGER,
            descricao TEXT,
            FOREIGN KEY (membro_id) REFERENCES membros (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    total_membros = conn.execute("SELECT COUNT(*) FROM membros").fetchone()[0]
    total_entradas = conn.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Entrada'").fetchone()[0] or 0.0
    total_saidas = conn.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'Saída'").fetchone()[0] or 0.0
    saldo = total_entradas - total_saidas
    
    membros = conn.execute("SELECT * FROM membros ORDER BY id DESC LIMIT 5").fetchall()
    transacoes = conn.execute('''
        SELECT t.*, m.nome as membro_nome 
        FROM transacoes t 
        LEFT JOIN membros m ON t.membro_id = m.id 
        ORDER BY t.id DESC LIMIT 5
    ''').fetchall()
    
    todos_membros = conn.execute("SELECT id, nome FROM membros ORDER BY nome ASC").fetchall()
    conn.close()
    
    return render_template('index.html', 
                           total_membros=total_membros, 
                           entradas=total_entradas, 
                           saidas=total_saidas, 
                           saldo=saldo,
                           membros=membros, 
                           transacoes=transacoes,
                           todos_membros=todos_membros)

@app.route('/membro/adicionar', methods=['POST'])
def adicionar_membro():
    nome = request.form['nome']
    telefone = request.form['telefone']
    departamento = request.form['departamento']
    
    conn = get_db_connection()
    conn.execute("INSERT INTO membros (nome, telefone, departamento) VALUES (?, ?, ?)",
                 (nome, telefone, departamento))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/transacao/adicionar', methods=['POST'])
def adicionar_transacao():
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    valor = float(request.form['valor'])
    membro_id = request.form.get('membro_id') or None
    descricao = request.form.get('descricao', '')
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO transacoes (tipo, categoria, valor, data, membro_id, descricao)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tipo, categoria, valor, data_atual, membro_id, descricao))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_conteudo)

print("✓ Ficheiro 'app.py' criado com sucesso!")
print("\nTudo pronto! Agora execute apenas: python app.py")