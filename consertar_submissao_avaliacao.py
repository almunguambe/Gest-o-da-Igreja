with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Localizar o bloco do formulário de avaliação
padrao_form = r'<form action="/discipulado/avaliar/\{\{ cid \}\}" method="POST">.*?</form>'

novo_form = '''<form id="formAvaliacao" action="/discipulado/avaliar/{{ cid }}" method="POST">
                        <input type="hidden" name="membro_id" value="{{ membro_id_aluno }}">
                        
                        <div class="alert alert-primary d-flex align-items-center mb-4 p-3 rounded-3" style="font-size: 0.95rem;">
                            <span class="me-2 fs-5">👤</span>
                            <div><strong>Candidato / Aluno:</strong> {{ nome_aluno_ativo }}</div>
                        </div>

                        {% for q in classe.questionario %}
                        <div class="mb-4 pb-3 border-bottom questao-bloco" id="bloco_q_{{ q.id }}">
                            <p class="fw-bold text-dark mb-2" style="font-size: 1.05rem;">{{ loop.index }}. {{ q.pergunta }}</p>
                            {% for op in q.opcoes %}
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="resp_{{ q.id }}" value="{{ loop.index0 }}" id="q_{{ q.id }}_{{ loop.index0 }}">
                                <label class="form-check-label text-secondary" for="q_{{ q.id }}_{{ loop.index0 }}" style="font-size: 1rem;">{{ op }}</label>
                            </div>
                            {% endfor %}
                            <div class="text-danger small mt-1 d-none aviso-obrigatorio" id="aviso_q_{{ q.id }}">⚠️ Por favor, selecione uma resposta para esta pergunta antes de submeter.</div>
                        </div>
                        {% endfor %}

                        <div class="d-flex justify-content-between align-items-center mt-4">
                            <a href="/discipulado/classe/{{ cid }}/licao/0" class="btn btn-outline-secondary">« Rever Lições</a>
                            <button type="submit" id="btnSubmeter" class="btn btn-primary fw-bold px-4 py-3 rounded-3 shadow">
                                <span>Submeter Respostas e Concluir Classe »</span>
                            </button>
                        </div>
                    </form>

                    <script>
                    document.getElementById('formAvaliacao').addEventListener('submit', function(e) {
                        var questoes = document.querySelectorAll('.questao-bloco');
                        var primeiraNaoRespondida = null;

                        questoes.forEach(function(bloco) {
                            var radios = bloco.querySelectorAll('input[type="radio"]');
                            var respondida = false;
                            radios.forEach(function(r) { if(r.checked) respondida = true; });
                            
                            var aviso = bloco.querySelector('.aviso-obrigatorio');
                            if (!respondida) {
                                if (aviso) aviso.classList.remove('d-none');
                                if (!primeiraNaoRespondida) primeiraNaoRespondida = bloco;
                            } else {
                                if (aviso) aviso.classList.add('d-none');
                            }
                        });

                        if (primeiraNaoRespondida) {
                            e.preventDefault();
                            primeiraNaoRespondida.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            return false;
                        }

                        var btn = document.getElementById('btnSubmeter');
                        btn.disabled = true;
                        btn.innerHTML = '<span>⏳ A processar notas...</span>';
                    });
                    </script>'''

conteudo = re.sub(padrao_form, novo_form, conteudo, flags=re.DOTALL)

# 2. Na rota que renderiza a avaliação, obter o nome e membro_id do aluno logado
rota_antiga = "return render_template_string(html, classe=classe, cid=cid)"
rota_nova = """
    # Identificar aluno pela sessao
    usuario_sessao = session.get('usuario', '')
    nome_aluno = usuario_sessao or 'Candidato IEAD'
    m_id_ativo = 1
    
    try:
        conn_aluno = get_db_connection()
        cur_aluno = conn_aluno.cursor()
        cur_aluno.execute("SELECT id, nome FROM membros WHERE LOWER(TRIM(nome)) LIKE LOWER(?) OR LOWER(TRIM(telefone)) = LOWER(?)", (f"%{usuario_sessao}%", usuario_sessao))
        m_row = cur_aluno.fetchone()
        if m_row:
            m_id_ativo = m_row[0] if isinstance(m_row, (tuple, list)) else m_row['id']
            nome_aluno = m_row[1] if isinstance(m_row, (tuple, list)) else m_row['nome']
        conn_aluno.close()
    except Exception:
        pass

    return render_template_string(html, classe=classe, cid=cid, membro_id_aluno=m_id_ativo, nome_aluno_ativo=nome_aluno)
"""

if rota_antiga in conteudo:
    conteudo = conteudo.replace(rota_antiga, rota_nova)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ Submissão de avaliação e identificação de aluno atualizadas com sucesso!")