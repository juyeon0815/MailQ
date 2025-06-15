# app/core/graph_client.py
import os
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import requests

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

def get_graph_token():
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY_URL
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in result:
        raise Exception(f"[Graph Auth Error] {result.get('error_description')}")
    return result["access_token"]


def get_user_principal_name(token: str) -> str:
    """
    Access Token을 이용해 사용자 ID(email)를 가져옵니다.
    """
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("userPrincipalName")  # 또는 "mail"