with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

rota_dashboard_membros = '''
@app.route('/secretaria/dashboard_membros')
def dashboard_membros():
    conn = get_db()
    try:
        membros = conn.execute("SELECT * FROM membros").fetchall()
    except Exception:
        membros = []
    finally:
        conn.close()

    total = len(membros)
    homens = 0
    mulheres = 0
    batizados = 0
    nao_batizados = 0
    novos_convertidos = 0

    # Faixas etárias IEAD
    faixa_criancas = {'H': 0, 'M': 0}      # 0 a 13 anos
    faixa_adolescentes = {'H': 0, 'M': 0}  # 14 a 17 anos
    faixa_jovens = {'H': 0, 'M': 0}        # 18 a 35 anos
    faixa_adultos = {'H': 0, 'M': 0}       # 36 a 59 anos
    faixa_terceira = {'H': 0, 'M': 0}      # 60+ anos

    # Obreiros vs Membros
    obreiros_contagem = {'Pastores': 0, 'Presbíteros': 0, 'Evangelistas': 0, 'Diáconos': 0}
    
    # Estado civil e Departamentos
    estado_civil = {}
    departamentos = {}

    ano_atual = datetime.now().year

    for m in membros:
        gen = 'M' if (m['genero'] or '').strip().upper() in ['F', 'FEMININO', 'MULHER'] else 'H'
        if gen == 'H':
            homens += 1
        else:
            mulheres += 1

        st_esp = (m['status_espiritual'] or '').strip().lower()
        if 'batizado' in st_esp:
            batizados += 1
        elif 'convertido' in st_esp:
            novos_convertidos += 1
        else:
            nao_batizados += 1

        # Cálculo de Idade
        idade = 30 # Padrão caso não tenha data de nascimento
        dn = m['data_nascimento'] or ''
        try:
            if '-' in dn:
                partes = dn.split('-')
                ano_nasc = int(partes[0]) if len(partes[0]) == 4 else int(partes[2])
                idade = ano_atual - ano_nasc
            elif '/' in dn:
                partes = dn.split('/')
                ano_nasc = int(partes[2])
                idade = ano_atual - ano_nasc
        except Exception:
            pass

        if idade <= 13:
            faixa_criancas[gen] += 1
        elif 14 <= idade <= 17:
            faixa_adolescentes[gen] += 1
        elif 18 <= idade <= 35:
            faixa_jovens[gen] += 1
        elif 36 <= idade <= 59:
            faixa_adultos[gen] += 1
        else:
            faixa_terceira[gen] += 1

        # Posição / Cargo
        cargo = (m['cargo_lideranca'] or '').strip().lower()
        if 'pastor' in cargo: obreiros_contagem['Pastores'] += 1
        elif 'presb' in cargo: obreiros_contagem['Presbíteros'] += 1
        elif 'evang' in cargo: obreiros_contagem['Evangelistas'] += 1
        elif 'diac' in cargo: obreiros_contagem['Diáconos'] += 1

        # Departamentos
        dep = (m['departamento'] or 'Sem Departamento').strip()
        departamentos[dep] = departamentos.get(dep, 0) + 1

        # Estado Civil
        ec = (m['estado_civil'] or 'Não Informado').strip()
        estado_civil[ec] = estado_civil.get(ec, 0) + 1

    dados_dashboard = {
        'total': total,
        'homens': homens,
        'mulheres': mulheres,
        'batizados': batizados,
        'nao_batizados': nao_batizados,
        'novos_convertidos': novos_convertidos,
        'faixa_criancas': faixa_criancas,
        'faixa_adolescentes': faixa_adolescentes,
        'faixa_jovens': faixa_jovens,
        'faixa_adultos': faixa_adultos,
        'faixa_terceira': faixa_terceira,
        'obreiros': obreiros_contagem,
        'departamentos': departamentos,
        'estado_civil': estado_civil
    }

    return render_template('dashboard_membros.html', d=dados_dashboard)
'''

if "/secretaria/dashboard_membros" not in conteudo:
    conteudo += "\n" + rota_dashboard_membros
    print("✓ Rota /secretaria/dashboard_membros adicionada com sucesso ao app.py!")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)