with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Adiciona o botão no topo da aba da Secretaria
botao_secretaria = '''
                        <a href="/secretaria/dashboard_membros" target="_blank" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-black text-xs rounded-xl shadow transition flex items-center gap-2">
                            <span>📊</span> Raio-X da Membrezia
                        </a>
'''

if '/secretaria/dashboard_membros' not in conteudo:
    # Coloca junto ao botão de emitir relatório oficial
    conteudo = conteudo.replace('<a href="/secretaria/relatorio_oficial"', botao_secretaria + '\n                        <a href="/secretaria/relatorio_oficial"')
    print("✓ Botão Raio-X da Membrezia inserido no Dashboard!")

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)