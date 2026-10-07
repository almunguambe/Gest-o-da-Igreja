with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Substituir trecho da consulta
antigo_status = "WHERE status = {param}"
if antigo_status in code:
    print("Identificada consulta rígida com status.")

# Criar versão da rota homologar que nunca quebra por falta de 'status'
with open('consertar_tudo_censo.py', 'r', encoding='utf-8') as f_censo:
    # Apenas garantir a migração
    pass

import re
# Garantir que a migração execute logo no topo da rota
bloco_ajuste = """
    # Garantir colunas dinamicamente
    cols_garantir = [
        ("status", "VARCHAR(50) DEFAULT 'Ativo'"),
        ("igreja", "VARCHAR(150) DEFAULT 'IEAD Chicuque'"),
        ("telefone", "VARCHAR(50)"),
        ("bairro", "VARCHAR(100)"),
        ("batizado", "VARCHAR(20) DEFAULT 'Não'"),
        ("departamento", "VARCHAR(100) DEFAULT 'Geral'"),
        ("foto_path", "VARCHAR(255)")
    ]
    for c_nome, c_tipo in cols_garantir:
        try:
            if is_pg:
                cur.execute(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {c_nome} {c_tipo};")
            else:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {c_nome} {c_tipo};")
            conn.commit()
        except Exception:
            if is_pg:
                try: conn.rollback()
                except Exception: pass
"""

print("Pronto para teste!")