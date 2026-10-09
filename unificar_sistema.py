import os
import shutil
import ast
import re

print("=" * 65)
print("A UNIFICAR O PAINEL: SIDEBAR, SECRETARIA E PLANIFICAÇÃO...")
print("=" * 65)

# 1. BACKUPS DE SEGURANÇA
if os.path.exists('app.py'):
    shutil.copy('app.py', 'app.py.bak')
tpl_dash = os.path.join('templates', 'dashboard.html')
if os.path.exists(tpl_dash):
    shutil.copy(tpl_dash, tpl_dash + '.bak')

# -------------------------------------------------------------------
# 2. ATUALIZAR O APP.PY (Leitura de Planos no Dashboard + Redirecionamento)
# -------------------------------------------------------------------
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Leitor universal seguro de planificações
leitor_planos_sql = """
    # Leitura Universal e Segura de Planificacoes
    planos = []
    try:
        cur_pl = conn.cursor() if hasattr(conn, 'cursor') else conn
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass
        cur_pl.execute("SELECT id, departamento, tipo_evento, nome_actividade, data_prevista, frequencia, responsavel_directo, contacto, status FROM planificacoes ORDER BY id DESC")
        linhas_pl = cur_pl.fetchall()
        for l in linhas_pl:
            if hasattr(l, 'get'):
                item = {
                    'id': l.get('id'),
                    'departamento': l.get('departamento') or 'Geral',
                    'tipo_evento': l.get('tipo_evento') or 'Geral',
                    'nome_actividade': l.get('nome_actividade') or 'Actividade',
                    'data_prevista': l.get('data_prevista') or '---',
                    'frequencia': l.get('frequencia') or 'Pontual',
                    'responsavel_directo': l.get('responsavel_directo') or '---',
                    'contacto': l.get('contacto') or '',
                    'status': l.get('status') or 'Pendente'
                }
            else:
                item = {
                    'id': l[0],
                    'departamento': l[1] or 'Geral',
                    'tipo_evento': l[2] or 'Geral',
                    'nome_actividade': l[3] or 'Actividade',
                    'data_prevista': l[4] or '---',
                    'frequencia': l[5] or 'Pontual',
                    'responsavel_directo': l[6] or '---',
                    'contacto': l[7] or '',
                    'status': l[8] or 'Pendente'
                }
            planos.append(item)
    except Exception as e_pl:
        print("[AVISO LEITURA PLANOS]:", e_pl)
        planos = []
"""

# Substitui o bloco antigo de leitura no dashboard
app_code = re.sub(
    r"#\s*Leitura Dedicada e Segura de Planificacoes[\s\S]*?except Exception as err:[\s\S]*?planos = \[\]",
    leitor_planos_sql.strip(),
    app_code
)

# Garantir que o POST de planificação regressa à aba de secretaria dentro do painel
app_code = re.sub(
    r"return redirect\('/secretaria/planificacao/nova'\)",
    "return redirect('/?aba=secretaria')",
    app_code
)

# Validação do backend com AST
try:
    ast.parse(app_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("✓ Backend app.py configurado e validado!")
except SyntaxError as e:
    print(f"Erro em app.py: {e}")
    shutil.copy('app.py.bak', 'app.py')
    exit(1)

# -------------------------------------------------------------------
# 3. ATUALIZAR O DASHBOARD.HTML (INCORPORAR PLANIFICAÇÃO + REATIVAR SIDEBAR)
# -------------------------------------------------------------------
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    dash_html = f.read()

# Remover quaisquer tags onerror defeituosas inseridas anteriormente dentro do HTML
dash_html = re.sub(r'onerror="this\.onerror=null;[^"]*"', '', dash_html)

# Módulo visual de Planificação pronto para viver dentro da aba Secretaria
bloco_planificacao_unificado = """
<div id="modulo-planificacao-embutido" style="margin-top: 25px;">
    <div style="display: grid; grid-template-columns: 1fr 1.6fr; gap: 24px;">
        
        <!-- COLUNA ESQUERDA: FORMULÁRIO -->
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                <span>📌</span> Planificar Nova Actividade
            </h3>
            
            <form action="/secretaria/planificacao/nova" method="POST" style="margin-top: 15px;">
                <div style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Departamento</label>
                    <select name="departamento" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;" required>
                        <option value="Activista Cristã">Activista Cristã</option>
                        <option value="Escola Dominical">Escola Dominical</option>
                        <option value="Juventude">Juventude</option>
                        <option value="Senhoras">Senhoras</option>
                        <option value="Homens / Pais">Homens / Pais</option>
                        <option value="Evangelismo">Evangelismo</option>
                        <option value="Geral">Geral</option>
                    </select>
                </div>

                <div style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Tipo de Evento</label>
                    <select name="tipo_evento" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;" required>
                        <option value="Seminário">Seminário</option>
                        <option value="Conferência">Conferência</option>
                        <option value="Culto Especial">Culto Especial</option>
                        <option value="Vigília">Vigília</option>
                        <option value="Reunião">Reunião</option>
                    </select>
                </div>

                <div style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Nome da Actividade</label>
                    <input type="text" name="nome_actividade" placeholder="Ex: 1º Seminário de Liderança" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;" required>
                </div>

                <div style="display: flex; gap: 12px; margin-bottom: 14px;">
                    <div style="flex: 1;">
                        <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Data Prevista</label>
                        <input type="date" name="data_prevista" style="width: 100%; padding: 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                    </div>
                    <div style="flex: 1;">
                        <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Frequência</label>
                        <select name="frequencia" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;">
                            <option value="Pontual / Única">Pontual / Única</option>
                            <option value="Semanal">Semanal</option>
                            <option value="Mensal">Mensal</option>
                            <option value="Anual">Anual</option>
                        </select>
                    </div>
                </div>

                <div style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Responsável Directo</label>
                    <input type="text" name="responsavel_directo" placeholder="Ex: Odete Aguiar" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                </div>

                <div style="margin-bottom: 18px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 5px;">Contacto / WhatsApp</label>
                    <input type="text" name="contacto" placeholder="Ex: 841234567" style="width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                </div>

                <button type="submit" style="width: 100%; padding: 13px; background-color: #3730a3; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; transition: background 0.2s;">
                    Gravar Planificação
                </button>
            </form>
        </div>

        <!-- COLUNA DIREITA: TABELA DO CRONOGRAMA -->
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); overflow-x: auto;">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                <span>📊</span> Monitoramento do Cronograma Eclesiástico
            </h3>

            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 2px solid #e2e8f0; text-align: left; color: #475569;">
                        <th style="padding: 10px 8px;">Actividade / Depto</th>
                        <th style="padding: 10px 8px;">Data Prevista</th>
                        <th style="padding: 10px 8px;">Responsável & Contacto</th>
                        <th style="padding: 10px 8px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% if planificacoes or planos %}
                        {% for p in (planificacoes or planos) %}
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 12px 8px;">
                                <strong style="color: #1e293b;">{{ p.nome_actividade }}</strong><br>
                                <small style="color: #64748b;">{{ p.departamento }}</small>
                            </td>
                            <td style="padding: 12px 8px; color: #334155;">{{ p.data_prevista }}</td>
                            <td style="padding: 12px 8px;">
                                <span style="color: #1e293b; font-weight: 500;">{{ p.responsavel_directo }}</span><br>
                                <small style="color: #64748b;">{{ p.contacto }}</small>
                            </td>
                            <td style="padding: 12px 8px;">
                                <span style="background-color: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 700;">
                                    {{ p.status }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="4" style="text-align: center; padding: 35px; color: #94a3b8;">
                                Nenhuma actividade planificada ainda. Cadastre a primeira ao lado.
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

# Se a planificação ainda não estiver dentro do dashboard, insere na secção da Secretaria
if 'modulo-planificacao-embutido' not in dash_html:
    # Procura a secção da secretaria ou insere após o primeiro bloco de conteúdo
    if 'id="secao-secretaria"' in dash_html:
        dash_html = dash_html.replace('id="secao-secretaria">', 'id="secao-secretaria">\n' + bloco_planificacao_unificado, 1)
    elif 'Secretaria & Planos' in dash_html:
        # Insere próximo ao cabeçalho ou secção da secretaria
        dash_html = re.sub(
            r'(<div[^>]*class="[^"]*secretaria[^"]*"[^>]*>)',
            r'\1\n' + bloco_planificacao_unificado,
            dash_html,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        # Se não houver secção identificada, cria um contentor dedicado
        dash_html = dash_html.replace('</main>', '<div id="secao-secretaria" class="secao-painel" style="display:none;">' + bloco_planificacao_unificado + '</div>\n</main>', 1)

# -------------------------------------------------------------------
# 4. CONTROLADOR MESTRE DE NAVEGAÇÃO DA SIDEBAR (SEM ERROS DE JS)
# -------------------------------------------------------------------
script_navegacao_sidebar = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // 1. MAPEAMENTO SEGURO DOS ITENS DA SIDEBAR PARA OS SEUS CONTEÚDOS
    var itensSidebar = document.querySelectorAll('.sidebar a, .sidebar button, .sidebar-item, [onclick*="mostrar"], [onclick*="abrir"], [onclick*="tab"]');
    var secoesConteudo = document.querySelectorAll('main > div, .conteudo-secao, .tab-pane, .secao-painel, [id^="secao-"], [id^="aba-"]');

    function ativarAbaPorNome(nomeAba) {
        if (!nomeAba) return;
        nomeAba = nomeAba.toLowerCase().trim();

        // Alterna os cartões de conteúdo
        var encontrouSecao = false;
        secoesConteudo.forEach(function(sec) {
            var secId = (sec.id || '').toLowerCase();
            var secClasse = (sec.className || '').toLowerCase();
            if (secId.includes(nomeAba) || secClasse.includes(nomeAba)) {
                sec.style.display = 'block';
                encontrouSecao = true;
            } else if (secId.length > 0 || secClasse.includes('secao')) {
                sec.style.display = 'none';
            }
        });

        // Atualiza o destaque visual na sidebar
        itensSidebar.forEach(function(item) {
            var texto = item.innerText.toLowerCase();
            if (texto.includes(nomeAba)) {
                item.style.backgroundColor = '#2e1065';
                item.style.borderRadius = '8px';
            } else {
                item.style.backgroundColor = 'transparent';
            }
        });
    }

    // 2. LIGAR CLIQUES DA SIDEBAR DIRETAMENTE (SEM TELA PARALELA)
    itensSidebar.forEach(function(item) {
        item.addEventListener('click', function(e) {
            var texto = this.innerText.toLowerCase();
            if (texto.includes('secretaria') || texto.includes('planos')) {
                e.preventDefault();
                ativarAbaPorNome('secretaria');
                window.history.replaceState(null, null, '?aba=secretaria');
            } else if (texto.includes('culto')) {
                ativarAbaPorNome('culto');
            } else if (texto.includes('convertido')) {
                ativarAbaPorNome('convertido');
            } else if (texto.includes('escala') || texto.includes('púlpito')) {
                ativarAbaPorNome('escala');
            } else if (texto.includes('casamento')) {
                ativarAbaPorNome('casamento');
            } else if (texto.includes('óbito') || texto.includes('obito')) {
                ativarAbaPorNome('obito');
            } else if (texto.includes('caixa') || texto.includes('finança') || texto.includes('meta')) {
                ativarAbaPorNome('financa');
            }
        });
    });

    // 3. SE O LINK FORNECER ?aba=secretaria, ABRE DIRETAMENTE A SECRETARIA
    var params = new URLSearchParams(window.location.search);
    if (params.get('aba') === 'secretaria') {
        ativarAbaPorNome('secretaria');
    }

    // 4. PROTEÇÃO GLOBAL CONTRA FOTOS QUEBRADAS (SEM AFETAR O JAVASCRIPT)
    document.addEventListener('error', function(ev) {
        if (ev.target && ev.target.tagName === 'IMG') {
            ev.target.onerror = null;
            var nome = ev.target.alt || 'Membro';
            ev.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(nome) + '&background=3730a3&color=fff&size=128';
        }
    }, true);
});
</script>
"""

if 'controlador-navegacao-sidebar' not in dash_html:
    dash_html = dash_html + '\n<!-- controlador-navegacao-sidebar -->\n' + script_navegacao_sidebar

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("✓ templates/dashboard.html atualizado e unificado com sucesso!")
print("=" * 65)
print("✓ PROCESSO CONCLUÍDO!")
print("=" * 65)