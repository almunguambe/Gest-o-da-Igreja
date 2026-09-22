import urllib.request
import json

dados = [
    {"usuario": "admin", "senha": "chicuque123", "cargo": "Pastor Presidente"},
    {"usuario": "secretaria", "senha": "12345", "cargo": "Secretário"},
    {"usuario": "tesouraria", "senha": "senha12345", "cargo": "Tesoureiro"},
    {"usuario": "doutrina", "senha": "senha12345", "cargo": "Aluno"}
]

req = urllib.request.Request(
    "https://jsonblob.com/api/jsonBlob",
    data=json.dumps(dados).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        # A URL do cofre vem no cabeçalho 'Location'
        blob_url = response.headers.get("Location")
        if blob_url:
            print("✓ Cofre criado com sucesso!")
            print(f"URL: {blob_url}")
            with open("blob_url.txt", "w", encoding="utf-8") as f:
                f.write(blob_url)
        else:
            print("Resposta recebida, mas Location não encontrado.")
except Exception as e:
    print(f"Erro ao criar blob: {e}")