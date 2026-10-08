import os
import re

print("Iniciando a limpeza profunda...")

pasta = 'templates'
if os.path.exists(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                original = conteudo
                
                # 1. ESCONDER O CERTIFICADO NAS LIÇÕES
                if 'Lição' in conteudo or 'Sair da Sala' in conteudo:
                    # Oculta qualquer link ou botão que tenha a palavra Certificado
                    conteudo = re.sub(r'(<a[^>]*)(>.*?Certificado.*?</a>)', r'\1 style="display: none !important;"\2', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'(<button[^>]*)(>.*?Certificado.*?</button>)', r'\1 style="display: none !important;"\2', conteudo, flags=re.IGNORECASE)

                # 2. RESTAURAR A PLANIFICAÇÃO
                if 'Gravar Planificação' in conteudo or 'A Enviar' in conteudo:
                    # Apagar todos os scripts JavaScript problemáticos
                    conteudo = re.sub(r'<script>\s*document\.addEventListener.*?<\/script>', '', conteudo, flags=re.IGNORECASE | re.DOTALL)
                    
                    # Restaurar o formulário puro
                    conteudo = re.sub(r'<form[^>]*>', '<form action="/secretaria/planificacao/nova" method="POST">', conteudo, flags=re.IGNORECASE)
                    
                    # Restaurar o botão puro
                    conteudo = re.sub(r'<button[^>]*>.*?(Gravar|Enviar|ligar).*?<\/button>', '<button type="submit" style="width: 100%; padding: 12px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">Gravar Planificação</button>', conteudo, flags=re.IGNORECASE)
                    
                    # Injetar as etiquetas (names) para o Python conseguir ler
                    conteudo = re.sub(r'placeholder=["\'](Ex: Seminário.*?)["\']', r'name="nome_actividade" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'placeholder=["\'](Odete.*?)["\']', r'name="responsavel_directo" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'placeholder=["\'](825.*?)["\']', r'name="contacto" placeholder="\1"', conteudo, flags=re.IGNORECASE)
                    conteudo = re.sub(r'type=["\']date["\']', r'type="date" name="data_prevista"', conteudo, flags=re.IGNORECASE)

                if original != conteudo:
                    with open(caminho, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    print(f"✓ Ficheiro limpo e corrigido: {file}")

print("✓ Limpeza concluída! Formulários restaurados.")