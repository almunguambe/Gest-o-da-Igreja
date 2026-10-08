import os

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

funcao_certificado = """
# MOTOR DE EXTRAÇÃO PARA CERTIFICADOS EM PDF
def extrair_dados_membro(membro_id):
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        
        # Tenta extrair o membro da base de dados do Supabase
        try:
            cur.execute("SELECT * FROM membros WHERE id = %s", (membro_id,))
        except:
            # Fallback de segurança
            cur.execute("SELECT * FROM membros WHERE id = ?", (membro_id,))
            
        row = cur.fetchone()
        if row:
            # Junta os nomes das colunas com os valores
            cols = [desc[0] for desc in cur.description]
            return dict(zip(cols, row))
    except Exception as e:
        print("Erro ao extrair membro para certificado:", e)
    return None
"""

# Injetar apenas se ainda não existir
if "def extrair_dados_membro" not in code:
    idx = code.rfind("if __name__ ==")
    if idx != -1:
        code = code[:idx] + funcao_certificado + "\n\n" + code[idx:]
    else:
        code += "\n\n" + funcao_certificado
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Motor de Certificados (extrair_dados_membro) instalado com sucesso no app.py!")
else:
    print("✓ A função extrair_dados_membro já estava no sistema.")