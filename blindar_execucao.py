with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

alvo = "def execute(self, sql, params=None):"
novo = """def execute(self, sql, params=None):
        # [BLINDAGEM] Limpa o estado da transacao anterior para o PostgreSQL nao travar
        try:
            if hasattr(self, '_conn'):
                self._conn.rollback()
            elif hasattr(self._cur, 'connection'):
                self._cur.connection.rollback()
        except:
            pass
"""

if "[BLINDAGEM]" not in code:
    # Substituir em todas as ocorrências de execute() nas classes híbridas
    code = code.replace(alvo, novo)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ app.py blindado com sucesso contra transações abortadas!")
else:
    print("✓ A blindagem já estava aplicada.")