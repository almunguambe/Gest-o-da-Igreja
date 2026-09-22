import json
import urllib.request

api_key = "$2a$10$AnLf2hbmM0bjeYIxshoFV.U4TadUmDhFugTGzO7FvcuqgkFxbijPO"

# Dados iniciais a guardar na nuvem
dados_iniciais = [
    {"usuario": "admin", "senha": "chicuque123", "cargo": "Pastor Presidente"},
    {"usuario": "secretaria", "senha": "12345", "cargo": "Secretário"},
    {"usuario": "tesouraria", "senha": "senha12345", "cargo": "Tesoureiro"},
    {"usuario": "doutrina", "senha": "senha12345", "cargo": "Aluno"}
]

req = urllib.request.Request(
    "https://api.jsonbin.io/v3/b",
    data=json.dumps(dados_iniciais).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "X-Master-Key": api_key,
        "X-Bin-Name": "iead_chicuque_usuarios"
    }
)

try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        bin_id = res["metadata"]["id"]
        print("✓ Cofre criado com sucesso na nuvem!")
        print(f"BIN_ID={bin_id}")
        with open("bin_id.txt", "w", encoding="utf-8") as f:
            f.write(bin_id)
except Exception as e:
    print(f"Erro ao criar cofre: {e}")