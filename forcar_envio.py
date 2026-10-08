import os
import re

js_definitivo = """
<!-- GATILHO INFALÍVEL -->
<script>
document.addEventListener("DOMContentLoaded", function() {
    let btn = Array.from(document.querySelectorAll("button")).find(b => b.innerText.includes("Gravar Planifica"));
    if(btn) {
        btn.type = "button"; 
        btn.onclick = function(e) {
            e.preventDefault();
            btn.innerText = "A Enviar...";
            btn.style.opacity = "0.7";
            
            let form = document.createElement("form");
            form.method = "POST";
            form.action = "/secretaria/planificacao/nova";
            form.style.display = "none";
            
            // Garante que as listas suspensas (selects) têm nome
            let selects = document.querySelectorAll("select");
            if(selects.length >= 3) {
                if(!selects[0].name) selects[0].name = "departamento";
                if(!selects[1].name) selects[1].name = "tipo_evento";
                if(!selects[2].name) selects[2].name = "frequencia";
            }
            
            // Garante que a data tem nome
            let dt = document.querySelector("input[type='date']");
            if(dt && !dt.name) dt.name = "data_prevista";
            
            // Clona todos os campos preenchidos
            document.querySelectorAll("input, select").forEach(el => {
                let nome = el.name;
                if(!nome && el.placeholder) {
                    let p = el.placeholder.toLowerCase();
                    if(p.includes("ex:") || p.includes("semin")) nome = "nome_actividade";
                    if(p.includes("odete")) nome = "responsavel_directo";
                    if(p.includes("825")) nome = "contacto";
                }
                if(nome) {
                    let inp = document.createElement("input");
                    inp.type = "hidden";
                    inp.name = nome;
                    inp.value = el.value;
                    form.appendChild(inp);
                }
            });
            
            document.body.appendChild(form);
            form.submit();
        };
    }
});
</script>
"""

pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'Gravar Planificação' in conteudo:
                    # Limpa versoes antigas do gatilho se existirem
                    conteudo = re.sub(r'<!-- GATILHO INFALÍVEL -->.*?</script>', '', conteudo, flags=re.IGNORECASE|re.DOTALL)
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo.strip() + "\n\n" + js_definitivo)
                    print(f"✓ Gatilho injetado com sucesso no ficheiro: {file}")