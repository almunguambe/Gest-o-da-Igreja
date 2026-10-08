import os
import re

js_fetch = """
<!-- TECNOLOGIA AJAX FETCH -->
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Procura o botão (mesmo que tenha ficado com o nome 'A Enviar...')
    let btn = Array.from(document.querySelectorAll("button, a")).find(b => b.innerText.includes("Enviar") || b.innerText.includes("Gravar Planifica"));
    
    if(btn) {
        // Substitui o botão por um novo e limpo
        let novoBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(novoBtn, btn);
        novoBtn.innerText = "Gravar Planificação";
        
        novoBtn.addEventListener("click", async function(e) {
            e.preventDefault();
            novoBtn.innerText = "A ligar ao Supabase...";
            novoBtn.style.backgroundColor = "#059669"; // Fica verde para sabermos que ativou
            novoBtn.style.color = "white";
            
            // Cria o pacote de dados
            let fd = new FormData();
            
            // Recolhe selects por ordem
            let selects = document.querySelectorAll("select");
            if(selects.length >= 3) {
                fd.append("departamento", selects[0].value);
                fd.append("tipo_evento", selects[1].value);
                fd.append("frequencia", selects[2].value);
            }
            
            // Recolhe a data
            let dt = document.querySelector("input[type='date']");
            if(dt) fd.append("data_prevista", dt.value);
            
            // Recolhe os textos pelo texto de ajuda (placeholder)
            document.querySelectorAll("input").forEach(inp => {
                let p = (inp.placeholder || "").toLowerCase();
                if(p.includes("ex:") || p.includes("semin")) fd.append("nome_actividade", inp.value);
                if(p.includes("odete")) fd.append("responsavel_directo", inp.value);
                if(p.includes("825")) fd.append("contacto", inp.value);
            });
            
            // Dispara pelos bastidores (Ignora o bloqueio do navegador)
            try {
                await fetch('/secretaria/planificacao/nova', { method: 'POST', body: fd });
                window.location.reload(); // Força o recarregamento da página
            } catch(error) {
                novoBtn.innerText = "Erro de Ligação!";
            }
        });
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
                
                # Se for a página da planificação
                if 'Gravar Planificação' in conteudo or 'A Enviar' in conteudo:
                    # Remove tentativas antigas
                    conteudo = re.sub(r'<!-- GATILHO INFALÍVEL -->.*?</script>', '', conteudo, flags=re.IGNORECASE|re.DOTALL)
                    conteudo = re.sub(r'<!-- SUPER MOTOR DE GRAVACAO -->.*?</script>', '', conteudo, flags=re.IGNORECASE|re.DOTALL)
                    
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo.strip() + "\n\n" + js_fetch)
                    print(f"✓ Tecnologia AJAX injetada com sucesso no ficheiro: {file}")

print("✓ O Botão agora ignora o navegador e comunica diretamente com o servidor!")