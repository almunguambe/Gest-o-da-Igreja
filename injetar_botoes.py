import os

# Adicionar atalho no menu/dashboard se existir templates
templates_dir = "templates"
if os.path.exists(templates_dir):
    for arq in os.listdir(templates_dir):
        if arq.endswith(".html"):
            caminho = os.path.join(templates_dir, arq)
            with open(caminho, "r", encoding="utf-8") as f:
                html = f.read()

            alterado = False
            # Injetar link para o Manual Semestral no menu se ainda não estiver
            if "/manual_doutrina_semestral" not in html and "href=\"/membros\"" in html:
                html = html.replace("href=\"/membros\"", "href=\"/manual_doutrina_semestral\" class=\"btn btn-warning btn-sm me-2\">📖 Manual Doutrina (6 Meses)</a><a href=\"/membros\"")
                alterado = True

            # Injetar botões de PDF nos detalhes do membro
            if "certificado_batismo" not in html and "membro.id" in html:
                botoes_pdf = '''
                <div class="btn-group my-2" role="group">
                    <a href="/membro/{{ membro.id }}/certificado_batismo" target="_blank" class="btn btn-primary btn-sm">📜 Certificado de Batismo</a>
                    <a href="/membro/{{ membro.id }}/carta_recomendacao" target="_blank" class="btn btn-secondary btn-sm">✉️ Carta Recomendação</a>
                    <a href="/membro/{{ membro.id }}/cartao_membro" target="_blank" class="btn btn-info btn-sm text-white">💳 Cartão de Membro</a>
                </div>
                '''
                if "Editar" in html or "Voltar" in html:
                    html = html.replace("Editar", botoes_pdf + "\nEditar")
                    alterado = True

            if alterado:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(html)

print("✓ Botões e atalhos injetados com sucesso nos formulários!")