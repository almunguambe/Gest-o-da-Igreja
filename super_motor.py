import os

js_injetar = """
<!-- SUPER MOTOR DE GRAVACAO -->
<script>
document.addEventListener("DOMContentLoaded", function() {
    // 1. Procurar o botao de gravar
    let botoes = document.querySelectorAll("button, a");
    let btnGravar = null;
    for(let b of botoes) {
        if(b.innerText && b.innerText.includes("Gravar Planifica")) {
            btnGravar = b;
            break;
        }
    }
    
    if(btnGravar) {
        // 2. Limpar qualquer bloqueio invisivel substituindo o botao
        let novoBtn = btnGravar.cloneNode(true);
        btnGravar.parentNode.replaceChild(novoBtn, btnGravar);
        
        // 3. Criar a ordem absoluta de envio
        novoBtn.addEventListener("click", function(e) {
            e.preventDefault();
            novoBtn.innerText = "A gravar... Aguarde!";
            novoBtn.style.opacity = "0.6";
            
            let form = document.createElement("form");
            form.method = "POST";
            form.style.display = "none";
            
            // 4. Apanhar todos os campos que o Anselmo preencheu
            let inputs = document.querySelectorAll("input, select, textarea");
            inputs.forEach(inp => {
                let name = inp.name || inp.id;
                let placeholder = (inp.placeholder || "").toLowerCase();
                
                // Se o campo não tiver nome no código HTML, deduz pelo texto de ajuda
                if(!name) {
                    if(placeholder.includes("semin") || placeholder.includes("ex:")) name = "nome_actividade";
                    else if(placeholder.includes("odete") || placeholder.includes("respons")) name = "responsavel_directo";
                    else if(placeholder.includes("825") || placeholder.includes("contact")) name = "contacto";
                }
                
                if(name) {
                    let hidden = document.createElement("input");
                    hidden.type = "hidden";
                    hidden.name = name;
                    hidden.value = inp.value;
                    form.appendChild(hidden);
                }
            });
            
            // 5. Enviar para a base de dados
            document.body.appendChild(form);
            form.submit();
        });
    }
});
</script>
"""

pasta = 'templates'
resolvido = False
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'Gravar Planificação' in conteudo and 'SUPER MOTOR' not in conteudo:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo + "\n" + js_injetar)
                    print(f"✓ Super Motor ativado no ficheiro: {file}")
                    resolvido = True

if resolvido:
    print("✓ O Botão está agora blindado e forçado a comunicar!")
else:
    print("O motor já estava instalado ou o ficheiro não foi encontrado.")