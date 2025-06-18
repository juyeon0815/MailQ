from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from bot.teams_bot import TeamsMailBot  # ← 여기 경로 확인
from flask import Flask, request, redirect
import requests
import urllib.parse
from util.token_helper import save_token, get_token ,save_conversation_reference, get_conversation_reference
from dotenv import load_dotenv
import asyncio
import os

app = Flask(__name__)
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
    token_json = response.json()
    
    user_id = request.args.get("state")
    save_token(user_id, token_json["access_token"])

    # ✅ 봇에게 메시지 보내기
    conversation_reference = get_conversation_reference(user_id)  # 저장된 ref
    if not conversation_reference:
        return "❗ 대화 정보가 없습니다. 봇에게 먼저 메시지를 보내 로그인 링크를 받아야 합니다.", 400

    async def send_to_teams():
        async def logic(context: TurnContext):
            await context.send_activity("✅ Microsoft 로그인이 완료되었습니다! 이제부터 Teams에서 메일 관련 작업을 도와드릴게요. 요약 요청을 하거나 메일 검색을 해보세요!")
        await adapter.continue_conversation(
            conversation_reference,
            logic,
            APP_ID
        )

     # ✅ 해결: 새 이벤트 루프 생성 후 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_teams())
    loop.close()
    
    return "✅ 로그인 완료! 이제 Teams로 안내 메시지가 발송됩니다."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3978)
