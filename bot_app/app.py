from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from bot.teams_bot import TeamsMailBot  # ← 여기 경로 확인
from flask import Flask, request, redirect
import requests
import urllib.parse
from util.token_helper import get_conversation_reference
from dotenv import load_dotenv
import asyncio
import os
import time
from util.token_helper import FileTokenStore

app = Flask(__name__)
token_store = FileTokenStore()
loop = asyncio.get_event_loop()


load_dotenv()

APP_ID = os.getenv("MICROSOFT_APP_ID")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD")
TENANT_ID = os.getenv("TENANT_ID")
DOMAIN = os.getenv("DOMAIN")
REDIRECT_URI = f"{DOMAIN}/auth/callback"
SCOPES = "offline_access User.Read Mail.Read"

# Adapter 설정
adapter_settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD
)

adapter = BotFrameworkAdapter(adapter_settings)
bot = TeamsMailBot()

@app.before_request
def maybe_cleanup_tokens():
    if time.time() % 300 < 1:
        token_store.cleanup_expired_tokens()


@app.route("/api/messages", methods=["POST"])
async def messages():
    activity = Activity().deserialize(request.json) #Teams에서 받은 메시지 파싱
    auth_header = request.headers.get("Authorization", "")
    
    await adapter.process_activity(activity, auth_header, bot.on_turn)
    
    return Response("OK", status=200)


@app.route("/auth/login")
def login():
    user_id = request.args.get("user_id")
    auth_url = (
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
        f"client_id={APP_ID}&response_type=code&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_mode=query&scope={urllib.parse.quote(SCOPES)}&state={urllib.parse.quote(user_id)}"
    )
    return redirect(auth_url)

@app.route("/auth/callback")
def callback():
    code = request.args.get("code")
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    data = {
        "client_id": APP_ID,
        "client_secret": APP_PASSWORD,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }

    response = requests.post(token_url, data=data)
    
    # 🔍 응답이 JSON이 아닐 수도 있으므로 try/catch 추가
    try:
        token_json = response.json()
    except Exception:
        return f"❌ Token 응답을 JSON으로 파싱할 수 없습니다:\n{response.text}", 400

    # ✅ access_token 확인
    access_token = token_json.get("access_token")
    if not access_token:
        return f"❌ access_token 없음: {token_json}", 400

    user_id = request.args.get("state")

    token_store.save_token(user_id, access_token, token_json.get("expires_in", 3600))


    # ✅ 봇에게 메시지 보내기
    conversation_reference = get_conversation_reference(user_id)
    if not conversation_reference:
        return "✅ 로그인 완료! 이제 Teams로 돌아가서 대화를 시작해주세요.", 200

    async def send_to_teams():
        async def logic(context: TurnContext):
            await context.send_activity("✅ Microsoft 로그인이 완료되었습니다! 이제부터 Teams에서 메일 관련 작업을 도와드릴게요.")
        await adapter.continue_conversation(
            conversation_reference,
            logic,
            APP_ID
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_teams())
    loop.close()
    
    return "✅ 로그인 완료! 이제 Teams로 돌아가서 대화를 시작해주세요.", 200
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=3978)
