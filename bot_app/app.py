from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from bot.teams_bot import TeamsMailBot  # ← 여기 경로 확인

import asyncio
import os

app = Flask(__name__)
loop = asyncio.get_event_loop()


# Adapter 설정
adapter_settings = BotFrameworkAdapterSettings(
    # app_id=os.getenv("MICROSOFT_APP_ID"),
    # app_password=os.getenv("MICROSOFT_APP_PASSWORD")
    app_id="",  # Microsoft App ID
    app_password=""  # Microsoft App Password
)

adapter = BotFrameworkAdapter(adapter_settings)
bot = TeamsMailBot()


@app.route("/api/messages", methods=["POST"])
async def messages():
    activity = Activity().deserialize(request.json) #Teams에서 받은 메시지 파싱
    auth_header = request.headers.get("Authorization", "")
    
    await adapter.process_activity(activity, auth_header, bot.on_turn)
   
    # task = loop.create_task(call_bot()) # 봇에게 메시지 전달
    # loop.run_until_complete(task)
    
    return Response("OK", status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3978)
