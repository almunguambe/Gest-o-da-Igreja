import os

estudos_path = os.path.join("templates", "estudos.html")

with open(estudos_path, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui qualquer chamada anterior de WhatsApp para apontar diretamente para o numero 258866677810
antigo_bloco_js = """        function enviarWhatsAppPastor() {
            const licao = encodeURIComponent(document.getElementById('campoLicaoDuvida').value);
            const duvida = encodeURIComponent(document.getElementById('textoDuvida').value);
            if (!duvida) {
                alert('Por favor, escreva a sua dúvida primeiro.');
                return;
            }
            const msg = `Paz do Senhor Pastor, sou o(a) candidato(a) ${encodeURIComponent("{{ session['usuario'] }}")} da IEAD Chicuque. Estou na lição [${licao}] e tenho a seguinte dúvida: ${duvida}`;
            window.open('https://wa.me/258840000000?text=' + msg, '_blank');
        }"""

novo_bloco_js = """        function enviarWhatsAppPastor() {
            const licao = encodeURIComponent(document.getElementById('campoLicaoDuvida').value);
            const duvida = encodeURIComponent(document.getElementById('textoDuvida').value);
            if (!duvida) {
                alert('Por favor, escreva a sua dúvida primeiro.');
                return;
            }
            const msg = `Paz do Senhor, sou o(a) candidato(a) ${encodeURIComponent("{{ session['usuario'] }}")} da IEAD Chicuque. Estou na lição [${licao}] e tenho a seguinte dúvida: ${duvida}`;
            window.open('https://wa.me/258866677810?text=' + msg, '_blank');
        }"""

html = html.replace(antigo_bloco_js, novo_bloco_js)
# Garante também caso já tenha a variável dinâmica telPastor
html = html.replace("https://wa.me/${telPastor}", "https://wa.me/258866677810")

with open(estudos_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✓ templates/estudos.html apontado com sucesso para o WhatsApp 258866677810!")