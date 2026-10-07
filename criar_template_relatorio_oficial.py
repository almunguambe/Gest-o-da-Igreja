html_relatorio = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Relatório Anual - IEAD Moçambique (Ministério Thavane)</title>
    <style>
        body { font-family: "Times New Roman", Times, serif; font-size: 11pt; color: #000; margin: 30px; line-height: 1.3; }
        .cabecalho { text-align: center; margin-bottom: 20px; }
        .cabecalho h2 { font-size: 14pt; margin: 0; text-transform: uppercase; font-weight: bold; }
        .cabecalho h3 { font-size: 11pt; margin: 4px 0; font-style: italic; }
        .cabecalho h4 { font-size: 12pt; margin: 4px 0; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 10pt; }
        th, td { border: 1px solid #000; padding: 4px 6px; text-align: center; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .text-left { text-align: left; }
        .titulo-seccao { font-weight: bold; text-transform: uppercase; margin-top: 15px; margin-bottom: 6px; font-size: 11pt; border-bottom: 1px solid #000; padding-bottom: 2px; }
        .assinaturas { margin-top: 50px; display: flex; justify-content: space-between; text-align: center; }
        @media print {
            .no-print { display: none; }
            body { margin: 15mm; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 15px;">
        <button onclick="window.print()" style="padding: 8px 16px; background: #1e3a8a; color: white; font-weight: bold; border-radius: 6px; cursor: pointer;">🖨️ Imprimir / Guardar em PDF</button>
    </div>

    <div class="cabecalho">
        <img src="/static/logo.png" style="max-height: 75px; margin-bottom: 5px;" onerror="this.style.display='none'">
        <h2>Igreja Evangélica Assembleia de Deus em Moçambique</h2>
        <h3>"Quando orardes, lembrai-vos de Moçambique! Remember Mozambique when you pray"</h3>
        <h4>Ministério Thavane • Província de Inhambane • Distrito de Maxixe</h4>
        <div style="font-weight: bold; margin-top: 10px; font-size: 13pt;">RELATÓRIO ANUAL E ESTATÍSTICA ECLESIÁSTICA</div>
    </div>

    <div class="titulo-seccao">1. Apresentação da Estrutura Distrital</div>
    <table>
        <tr><th class="text-left">Função</th><th class="text-left">Nome Completo</th><th class="text-left">Contacto</th></tr>
        <tr><td class="text-left">Pastor Presidente / Coordenador</td><td class="text-left">Pastor Distrital</td><td class="text-left">-</td></tr>
        <tr><td class="text-left">Secretário Distrital</td><td class="text-left">Romão Semende Savanguane (Evangelista)</td><td class="text-left">-</td></tr>
        <tr><td class="text-left">Tesoureiro Distrital</td><td class="text-left">Tesoureiro em Exercício</td><td class="text-left">-</td></tr>
    </table>

    <div class="titulo-seccao">2. Estatística Geral Eclesiástica (Discriminada por Género)</div>
    <table>
        <thead>
            <tr>
                <th rowspan="2">Designação</th>
                <th colspan="3">Membros Existentes</th>
                <th colspan="3">Novos / Conversões / Baptismos</th>
                <th colspan="3">Total Geral</th>
            </tr>
            <tr>
                <th>H</th><th>M</th><th>Total</th>
                <th>H</th><th>M</th><th>Total</th>
                <th>H</th><th>M</th><th>Total</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="text-left">Obreiros (Pastores, Presbíteros, Evangelistas, Diáconos)</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
            </tr>
            <tr>
                <td class="text-left">Membros Baptizados Adultos</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
            </tr>
            <tr>
                <td class="text-left">Juventude Cristã (18 a 35 anos)</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
            </tr>
            <tr>
                <td class="text-left">Boa Esperança (Adolescentes e Crianças)</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
                <td>-</td><td>-</td><td>-</td>
            </tr>
        </tbody>
    </table>

    <div class="titulo-seccao">3. Monitoramento de Actividades Planificadas e Realizadas</div>
    <table>
        <thead>
            <tr>
                <th class="text-left">Actividade</th>
                <th class="text-left">Departamento</th>
                <th>Data Realiz.</th>
                <th>Participantes (H / M / J / C)</th>
                <th class="text-left">Temas Abordados / Resultados</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for p in planos %}
            <tr>
                <td class="text-left font-bold">{{ p['actividade'] }}</td>
                <td class="text-left">{{ p['departamento'] }}</td>
                <td>{{ p['data_realizacao'] or p['data_prevista'] }}</td>
                <td>{{ p['homens_participantes'] or 0 }}H / {{ p['mulheres_participantes'] or 0 }}M / {{ p['jovens_participantes'] or 0 }}J / {{ p['criancas_participantes'] or 0 }}C</td>
                <td class="text-left">
                    {% if p['temas_abordados'] %}<div><strong>Temas:</strong> {{ p['temas_abordados'] }}</div>{% endif %}
                    {% if p['decisoes_convertidos'] %}<div><strong>Decisões:</strong> {{ p['decisoes_convertidos'] }} convertidos</div>{% endif %}
                </td>
                <td>{{ p['status'] }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6">Sem registo de actividades.</td></tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="assinaturas">
        <div>
            ____________________________________________<br>
            <strong>Visto do Pastor Presidente / Coordenador</strong>
        </div>
        <div>
            ____________________________________________<br>
            <strong>O Secretário Distrital</strong><br>
            Romão Semende Savanguane //Evangelista//
        </div>
    </div>
</body>
</html>
'''

with open('templates/relatorio_oficial_modelo.html', 'w', encoding='utf-8') as f:
    f.write(html_relatorio)

print("✓ Template relatorio_oficial_modelo.html criado com fidelidade ao modelo Thavane!")