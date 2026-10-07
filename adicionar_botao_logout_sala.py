with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Adicionar o botão "Sair da Sala" na barra superior das Lições de Discipulado
barra_licoes_antiga = """                <div class="d-flex gap-2">
                    <span class="badge bg-white text-dark border px-3 py-2 fw-semibold">Lição {{ lid + 1 }} de {{ total_licoes }}</span>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-sm btn-success fw-bold">🎓 Certificado</a>
                    {% endif %}
                </div>"""

barra_licoes_nova = """                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-white text-dark border px-3 py-2 fw-semibold">Lição {{ lid + 1 }} de {{ total_licoes }}</span>
                    {% if concluiu_todas %}
                    <a href="/membro/{{ m_id }}/certificado_conclusao_discipulado" target="_blank" class="btn btn-sm btn-success fw-bold">🎓 Certificado</a>
                    {% endif %}
                    <a href="/logout" class="btn btn-sm btn-outline-danger fw-bold px-3 py-1 shadow-sm d-flex align-items-center gap-1" title="Encerrar sessão e voltar ao login">
                        <span>🚪</span> Sair da Sala
                    </a>
                </div>"""

# Substitui com tolerância a espaços
import re

conteudo = re.sub(
    r'<div class="d-flex gap-2">\s*<span class="badge bg-white text-dark border px-3 py-2 fw-semibold">Lição \{\{ lid \+ 1 \}\} de \{\{ total_licoes \}\}</span>\s*\{% if concluiu_todas %\}.*?\{% endif %}\s*</div>',
    barra_licoes_nova,
    conteudo,
    flags=re.DOTALL
)

# 2. Adicionar o botão "Sair da Sala" no topo da Prova / Avaliação
header_prova_antigo = """                <div class="card-header-prova">
                    <h3 class="fw-bold mb-1">📝 Prova de Avaliação</h3>
                    <div class="text-light">{{ classe.nome }} • Questionário Oficial</div>
                </div>"""

header_prova_novo = """                <div class="card-header-prova d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <div>
                        <h3 class="fw-bold mb-1">📝 Prova de Avaliação</h3>
                        <div class="text-light">{{ classe.nome }} • Questionário Oficial</div>
                    </div>
                    <div>
                        <a href="/logout" class="btn btn-sm btn-outline-light fw-bold px-3 py-2 shadow-sm d-flex align-items-center gap-1">
                            <span>🚪</span> Sair da Sala
                        </a>
                    </div>
                </div>"""

conteudo = conteudo.replace(header_prova_antigo, header_prova_novo)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Botão 'Sair da Sala' integrado com sucesso nas lições e nas avaliações!")