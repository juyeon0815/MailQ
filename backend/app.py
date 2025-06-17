from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import AzureOpenAI
from dotenv import load_dotenv 
import os
import requests
import msal


app = Flask(__name__)
CORS(app)

load_dotenv()
# Azure OpenAI 설정
endpoint = os.getenv("OPENAI_API_ENDPOINT")
model_name = os.getenv("MODEL_MODE")
deployment = os.getenv("DEPLOYMENT_NAME")

api_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("OPENAI_API_VERSION")

# client = AzureOpenAI(
#     api_version=api_version,
#     azure_endpoint=endpoint,
#     api_key=api_key,
# )

# response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant.",
#         },
#         {
#             "role": "user",
#             "content": "I am going to Paris, what should I see?",
#         }
#     ],
#     model=deployment
# )

# print(response.choices[0].message.content)


########################################################################
# 이메일 수집
# === Azure 앱 등록 정보 ===
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

# === Microsoft Graph 설정 ===
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read"]

# === 2. MSAL 앱 초기화 ===
app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)

# === 3. 캐시된 계정 확인 후 silent login 시도 ===
accounts = app.get_accounts()
if accounts:
    for account in accounts:
        app.remove_account(account)  # 캐시된 계정 삭제
    # 계정 삭제 후에는 silent token 불가능하니, device flow로 재로그인 진행
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Device Flow 시작 실패. 앱 등록 정보를 확인하세요.")

    print("📌 아래 메시지에 따라 로그인 진행:")
    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)
else:
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Device Flow 시작 실패. 앱 등록 정보를 확인하세요.")

    print("📌 아래 메시지에 따라 로그인 진행:")
    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

import base64
import json

def decode_jwt(token):
    parts = token.split('.')
    payload = parts[1] + '=' * (-len(parts[1]) % 4)  # padding
    decoded_bytes = base64.urlsafe_b64decode(payload)
    return json.loads(decoded_bytes)

token_data = decode_jwt(result['access_token'])
print("토큰 권한(scope):", token_data.get('scp'))

# === 5. Access Token 획득 성공 시 메일 요청 ===
if "access_token" in result:
    headers = {
        "Authorization": f"Bearer {result['access_token']}",
        "Content-Type": "application/json"
    }

    print("\n📬 받은 편지함에서 최근 메일을 가져옵니다...")

    # url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=10"
    url = "https://graph.microsoft.com/v1.0/me/messages"
    res = requests.get(url, headers=headers)

    print(res.status_code)
    print(res.text)

    print(headers)


    if res.status_code == 200:
        for message in res.json().get("value", []):
            sender = message.get("from", {}).get("emailAddress", {}).get("name", "(알 수 없음)")
            subject = message.get("subject", "(제목 없음)")
            print(f"- 보낸사람: {sender}, 제목: {subject}")
    else:
        print("❌ 메일 요청 실패:", res.status_code, res.text)
else:
    print("❌ 토큰 획득 실패:", result.get("error_description"))


# @app.route("/summarize", methods=["POST"])
# def summarize():
#     email_body = request.json["email_body"]

#     response = openai.ChatCompletion.create(
#         engine=DEPLOYMENT_NAME,
#         messages=[
#             {"role": "system", "content": "You are an email assistant. Summarize the following email."},
#             {"role": "user", "content": email_body}
#         ],
#         temperature=0.5
#     )

#     summary = response["choices"][0]["message"]["content"]
#     return jsonify({"summary": summary})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
