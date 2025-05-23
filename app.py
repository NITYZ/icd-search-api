import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
API_BASE_URL = "https://id.who.int/icd/release/11"

app = FastAPI(
    title="ICD Search Plugin",
    description="Busca códigos CID (ICD-11) via API oficial da OMS.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def obter_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "icdapi_access"
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

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
        return {"erro": str(e)}
@app.get("/")
def root():
    return {"status": "API ICD está online 🚀"}
