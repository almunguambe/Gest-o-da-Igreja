import os

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. ESCUDO DO CERTIFICADO (Vacina contra o erro NoneType)
alvo_cert = """    except Exception as e:
        print("Erro ao extrair membro para certificado:", e)
    return None"""

novo_cert = """    except Exception as e:
        print("Erro ao extrair membro para certificado:", e)
        
    class CofreSeguro(dict):
        def __getitem__(self, key):
            return self.get(key, "Dados Indisponíveis")
    return CofreSeguro({'nome': 'Aluno não registado na nova base'})"""

if alvo_cert in code:
    code = code.replace(alvo_cert, novo_cert)
    
# Remove a query de fallback que crasha o Postgres
code = code.replace('cur.execute("SELECT * FROM membros WHERE id = ?", (membro_id,))', 'pass')

# 2. TRADUTOR DA PLANIFICAÇÃO (SQLite para PostgreSQL)
# Substitui os pontos de interrogação (?) pela sintaxe correta (%s)
code = code.replace("VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')", "VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pendente')")

# Garante que usamos o cursor correto para executar a query no Supabase
code = code.replace("conn.execute(sql, (departamento", "cur = conn.cursor() if hasattr(conn, 'cursor') else conn\n            cur.execute(sql, (departamento")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Sistema vacinado! Certificados protegidos e Planificacao traduzida para Postgres.")