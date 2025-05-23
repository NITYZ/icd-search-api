import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 📥 Carrega variáveis do .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 🚨 Verificação das variáveis de ambiente
if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError("CLIENT_ID e CLIENT_SECRET devem estar definidos no .env ou ambiente.")

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
API_BASE_URL = "https://id.who.int/icd/release/11"

# 🚀 Inicializa FastAPI
app = FastAPI(
    title="ICD Search Plugin",
    description="Busca códigos CID (ICD-11) via API oficial da OMS.",
    version="1.0.0"
)

# 🌐 Middleware de CORS liberado geral
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 Função para obter token de acesso
def obter_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "icdapi_access"
    }
    response = requests.post(TOKEN_URL, data=data)
    print("Token response status:", response.status_code)
    print("Token response body:", response.text)  # DEBUG
    response.raise_for_status()
    return response.json()["access_token"]

# 🔍 Endpoint de busca ICD
@app.get("/buscar_icd", operation_id="buscarICD", summary="Buscar códigos ICD pelo título")
def buscar_icd(titulo: str = Query(..., description="Título do trabalho clínico ou científico")):
    try:
        token = obter_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = requests.get(
            f"{API_BASE_URL}/search",
            headers=headers,
            params={"q": titulo, "linearization": "mms"}
        )
        response.raise_for_status()
        data = response.json()

        resultados = []
        for item in data.get("destinationEntities", [])[:5]:
            resultados.append({
                "codigo": item.get("code"),
                "titulo": item.get("title", {}).get("value"),
                "url": f"https://icd.who.int/browse11/l-m/en#/http://id.who.int/icd/entity/{item.get('id')}"
            })

        return {"resultados": resultados}
    except Exception as e:
        import traceback
        return {
            "erro": str(e),
            "stack": traceback.format_exc()
        }

# ✅ Endpoint raiz
@app.get("/")
def root():
    return {"status": "API ICD está online 🚀"}
