with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

rota_codigo = '''
@app.route('/secretaria/relatorio_oficial')
def ver_relatorio_oficial():
    conn = get_db()
    membros = []
    cultos = []
    planos = []
    casamentos = []
    
    try:
        membros = conn.execute("SELECT * FROM membros").fetchall()
    except Exception:
        pass
        
    try:
        cultos = conn.execute("SELECT * FROM cultos_frequencia ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    try:
        planos = conn.execute("SELECT * FROM actividades_planeamento ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    try:
        casamentos = conn.execute("SELECT * FROM casamentos ORDER BY id DESC").fetchall()
    except Exception:
        pass
        
    conn.close()
    return render_template('relatorio_oficial_modelo.html', membros=membros, cultos=cultos, planos=planos, casamentos=casamentos)
'''

# Se a rota já existir mas com outro formato ou se não existir, garantimos a presença correta
if "@app.route('/secretaria/relatorio_oficial')" in conteudo:
    import re
    conteudo = re.sub(r"@app\.route\('/secretaria/relatorio_oficial'\).*?(?=@app\.route|\Z)", rota_codigo.strip() + "\n\n", conteudo, flags=re.DOTALL)
    print("✓ Rota existente substituída e blindada contra ausência de dados!")
else:
    conteudo += "\n" + rota_codigo
    print("✓ Rota /secretaria/relatorio_oficial adicionada com sucesso ao final do app.py!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)