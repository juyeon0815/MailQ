# app/core/graph_client.py
import os
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import requests
import jwt  # PyJWT
from jwt import DecodeError
from botbuilder.core import TurnContext

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

def extract_access_token_from_context(turn_context: TurnContext) -> str:
    """
    Teams 채널 데이터에서 Outlook Graph API용 access_token 추출
    """
    try:
        return turn_context.activity.channel_data["tenant"]["token"]
    except KeyError:
        raise ValueError("Access token not found in channel_data")

# def get_user_email_from_token(access_token: str) -> str:
#     """
#     access_token 내부 디코딩하여 사용자의 이메일(upn) 추출
#     """
#     try:
#         decoded = jwt.decode(access_token, options={"verify_signature": False})
#         return decoded.get("upn") or decoded.get("preferred_username")
#     except DecodeError:
#         raise ValueError("Invalid access token")


async def get_user_principal_name(token: str) -> str:
    """
    Access Token을 이용해 사용자 ID(email)를 가져옵니다.
    """
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("userPrincipalName")  # 또는 "mail"