import os
import re

print("A aplicar o modo de Desempate...")

# 1. FORÇAR OS ERROS A APARECEREM NO ECRÃ (app.py)
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

nova_rota = """
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_nova():
    from flask import render_template, request, redirect
    
    try:
        conn = get_db()
    except Exception as e:
        return f"<h1 style='color:red;'>ERRO A LIGAR À BASE DE DADOS: {str(e)}</h1>"

    if request.method == 'POST':
        fd = request.form
        departamento = fd.get('departamento', 'Não definido')
        tipo_evento = fd.get('tipo_evento', 'Não definido')
        nome_actividade = fd.get('nome_actividade', 'Não definido')
        data_prevista = fd.get('data_prevista', '')
        frequencia = fd.get('frequencia', 'Não definido')
        responsavel = fd.get('responsavel_directo', 'Não definido')
        contacto = fd.get('contacto', 'Não definido')
        
        data_bd = data_prevista if data_prevista and data_prevista.strip() != '' else None
        
        try:
            cur = conn.cursor() if hasattr(conn, 'cursor') else conn
            sql = '''INSERT INTO planificacoes (departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')'''
            cur.execute(sql, (departamento, tipo_evento, nome_actividade, data_bd, frequencia, responsavel, contacto))
            if hasattr(conn, 'commit'):
                conn.commit()
            return redirect('/secretaria/planificacao/nova')
        except Exception as e:
            # SE A GRAVAÇÃO FALHAR, ISTO MOSTRA O ERRO NO ECRÃ!
            return f"<h1 style='color:red; text-align:center; margin-top:50px;'>O SUPABASE REJEITOU A GRAVAÇÃO:</h1><h2 style='text-align:center;'>{str(e)}</h2><p style='text-align:center;'>Tire foto deste erro e mande ao assistente.</p>"

    planos = []
    try:
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        cur.execute("SELECT * FROM planificacoes ORDER BY id DESC LIMIT 10")
        cols = [desc[0] for desc in cur.description] if cur.description else []
        planos = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception:
        pass 

    return render_template('nova_planificacao.html', planificacoes=planos)
"""

padrao_rota = r"@app\.route\('/secretaria/planificacao/nova'.*?(?=\n@app\.route|\nif __name__ ==)"
if re.search(padrao_rota, code, re.DOTALL):
    code = re.sub(padrao_rota, nova_rota.strip() + "\n\n", code, flags=re.DOTALL)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Rota da Planificação protegida: os erros agora vão aparecer no ecrã!")


# 2. ESCONDER CERTIFICADO E GARANTIR NOMES DOS CAMPOS (HTML)
js_carrasco = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // 1. Destruir botao do certificado nas licoes
    let textoPagina = document.body.innerText.toLowerCase();
    if(textoPagina.includes("lição 1") || window.location.href.toLowerCase().includes("licao")) {
        document.querySelectorAll("a, button").forEach(btn => {
            if(btn.innerText.toLowerCase().includes("certificado")) {
                btn.remove(); // Remove completamente do HTML
            }
        });
    }
    
    // 2. Garantir que os campos têm as etiquetas corretas para o Python
    let btnGravar = document.querySelector("button");
    if(btnGravar && btnGravar.innerText.includes("Gravar")) {
        btnGravar.type = "submit";
        
        document.querySelectorAll("input").forEach(inp => {
            let p = (inp.placeholder || "").toLowerCase();
            if(p.includes("semin") && !inp.name) inp.name = "nome_actividade";
            if(p.includes("odete") && !inp.name) inp.name = "responsavel_directo";
            if(p.includes("825") && !inp.name) inp.name = "contacto";
            if(inp.type === "date" && !inp.name) inp.name = "data_prevista";
        });
        
        document.querySelectorAll("select").forEach((sel, idx) => {
            if(!sel.name) {
                if(idx === 0) sel.name = "departamento";
                if(idx === 1) sel.name = "tipo_evento";
                if(idx === 2) sel.name = "frequencia";
            }
        });
    }
});
</script>
"""

pasta = 'templates'
for r, d, f in os.walk(pasta):
    for file in f:
        if file.endswith('.html'):
            path = os.path.join(r, file)
            with open(path, 'r', encoding='utf-8') as html_file:
                html = html_file.read()
            
            # Limpa todos os scripts anteriores que injetámos
            html = re.sub(r'<!-- SUPER MOTOR.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
            html = re.sub(r'<!-- GATILHO INFALÍVEL.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
            html = re.sub(r'<!-- TECNOLOGIA AJAX.*?</script>', '', html, flags=re.IGNORECASE|re.DOTALL)
            
            # Injeta o novo script limpo no final da página
            if "<script>document.addEventListener(\"DOMContentLoaded\", function() {\n    // 1. Destruir" not in html and "</body>" in html:
                html = html.replace("</body>", js_carrasco + "\n</body>")
                with open(path, 'w', encoding='utf-8') as html_file:
                    html_file.write(html)
                    
print("✓ HTML limpo: Certificados ocultos nas lições e formulários preparados.")