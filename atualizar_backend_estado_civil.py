with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

# 1. Garantir que a tabela membros tenha a coluna estado_civil
auto_coluna = """
    try:
        c.execute("ALTER TABLE membros ADD COLUMN estado_civil TEXT DEFAULT 'Solteiro(a)'")
    except: pass
"""
if "ADD COLUMN estado_civil" not in conteudo:
    conteudo = conteudo.replace("c.execute('''CREATE TABLE IF NOT EXISTS membros", auto_coluna + "\n    c.execute('''CREATE TABLE IF NOT EXISTS membros")

# 2. Atualizar a rota /secretaria/dashboard_membros para ler o estado_civil real
rota_dash_nova = '''@app.route('/secretaria/dashboard_membros')
def dashboard_membros():
    conn = get_db()
    membros = []
    try:
        # Garante a existência da coluna no PostgreSQL/SQLite
        try:
            conn.execute("ALTER TABLE membros ADD COLUMN estado_civil TEXT DEFAULT 'Solteiro(a)'")
            conn.commit()
        except: pass
        membros = conn.execute("SELECT * FROM membros").fetchall()
    except Exception as e:
        print("Erro ao ler membros:", e)
        membros = []
    finally:
        conn.close()

    total = len(membros)
    homens = 0
    mulheres = 0
    batizados = 0
    nao_batizados = 0
    novos_convertidos = 0

    faixa_criancas = {'H': 0, 'M': 0}      # 0 a 13 anos
    faixa_adolescentes = {'H': 0, 'M': 0}  # 14 a 17 anos
    faixa_jovens = {'H': 0, 'M': 0}        # 18 a 35 anos
    faixa_adultos = {'H': 0, 'M': 0}       # 36 a 59 anos
    faixa_terceira = {'H': 0, 'M': 0}      # 60+ anos

    obreiros_contagem = {'Pastores': 0, 'Presbíteros': 0, 'Evangelistas': 0, 'Diáconos': 0}
    estado_civil = {}
    departamentos = {}

    ano_atual = datetime.now().year

    for m in membros:
        item = dict(m) if hasattr(m, 'keys') else m

        # 1. Género
        raw_gen = str(item.get('genero') or item.get('sexo') or '').strip().lower()
        if raw_gen.startswith('f') or 'mulher' in raw_gen:
            gen = 'M'
            mulheres += 1
        else:
            gen = 'H'
            homens += 1

        # 2. Baptismo / Novos Convertidos
        dt_batismo = str(item.get('data_batismo') or '').strip()
        posicao = str(item.get('posicao_atual') or item.get('cargo_lideranca') or '').strip().lower()
        ano_conv = str(item.get('ano_conv') or '').strip()

        if dt_batismo and dt_batismo.lower() not in ['none', 'null', 'nan', '']:
            batizados += 1
        elif 'convertid' in posicao or (ano_conv and ano_conv == str(ano_atual)):
            novos_convertidos += 1
        else:
            nao_batizados += 1

        # 3. Faixas Etárias
        dn = str(item.get('data_nasc') or item.get('data_nascimento') or '').strip()
        segmento = str(item.get('segmento') or '').strip().lower()
        
        idade = None
        try:
            if '-' in dn:
                partes = dn.split('-')
                ano_nasc = int(partes[0]) if len(partes[0]) == 4 else int(partes[2])
                idade = ano_atual - ano_nasc
            elif '/' in dn:
                partes = dn.split('/')
                ano_nasc = int(partes[2]) if len(partes) >= 3 else 1990
                idade = ano_atual - ano_nasc
        except Exception:
            idade = None

        if idade is not None:
            if idade <= 13: faixa_criancas[gen] += 1
            elif 14 <= idade <= 17: faixa_adolescentes[gen] += 1
            elif 18 <= idade <= 35: faixa_jovens[gen] += 1
            elif 36 <= idade <= 59: faixa_adultos[gen] += 1
            else: faixa_terceira[gen] += 1
        else:
            if 'criança' in segmento: faixa_criancas[gen] += 1
            elif 'adolescente' in segmento: faixa_adolescentes[gen] += 1
            elif 'jovem' in segmento: faixa_jovens[gen] += 1
            elif 'idoso' in segmento or 'terceira' in segmento: faixa_terceira[gen] += 1
            else: faixa_adultos[gen] += 1

        # 4. Obreiros
        if 'pastor' in posicao: obreiros_contagem['Pastores'] += 1
        elif 'presb' in posicao: obreiros_contagem['Presbíteros'] += 1
        elif 'evang' in posicao: obreiros_contagem['Evangelistas'] += 1
        elif 'diac' in posicao: obreiros_contagem['Diáconos'] += 1

        # 5. Departamento
        dep = str(item.get('departamento') or 'Geral').strip()
        if not dep or dep.lower() in ['none', 'null', 'nan']: dep = 'Geral'
        departamentos[dep] = departamentos.get(dep, 0) + 1

        # 6. Estado Civil Real
        ec = str(item.get('estado_civil') or '').strip()
        if not ec or ec.lower() in ['none', 'null', 'nan']:
            ec = 'Não Informado'
        estado_civil[ec] = estado_civil.get(ec, 0) + 1

    perc_homens = round((homens / total * 100), 1) if total > 0 else 0
    perc_mulheres = round((mulheres / total * 100), 1) if total > 0 else 0

    dados_dashboard = {
        'total': total,
        'homens': homens,
        'mulheres': mulheres,
        'perc_homens': perc_homens,
        'perc_mulheres': perc_mulheres,
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

padrao_dash = r"@app\.route\('/secretaria/dashboard_membros'\).*?(?=@app\.route|\Z)"
conteudo = re.sub(padrao_dash, rota_dash_nova.strip() + "\n\n", conteudo, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ app.py atualizado com cálculo de percentuais e processamento de Estado Civil!")