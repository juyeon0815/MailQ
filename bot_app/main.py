import os
import asyncio
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    ActivityHandler,
    MessageFactory
)
from botbuilder.schema import Activity, ActivityTypes

class EchoBot(ActivityHandler):
    """
    간단한 에코 봇 클래스
    """
    
    async def on_message_activity(self, turn_context: TurnContext):
        """
        사용자 메시지에 응답하는 메서드
        """
        user_message = turn_context.activity.text
        reply_text = f"Echo: {user_message}"
        
        # 응답 메시지 생성 및 전송
        reply_activity = MessageFactory.text(reply_text)
        await turn_context.send_activity(reply_activity)

    async def on_members_added_activity(
        self, members_added, turn_context: TurnContext
    ):
        """
        새 멤버가 추가되었을 때 환영 메시지
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_message = "안녕하세요! 저는 에코 봇입니다. 메시지를 보내주시면 그대로 따라 말할게요."
                await turn_context.send_activity(MessageFactory.text(welcome_message))


# Bot Framework Adapter 설정
def create_adapter():
    """
    Bot Framework Adapter 생성
    """
    settings = BotFrameworkAdapterSettings(
        app_id="ef49f037-efa3-4680-a649-c78e26c6c673",
        app_password="0Sf8Q~9g9C33VDMkOJxA7562Wqu-FbMcT3Y19cs-"
    )
    
    adapter = BotFrameworkAdapter(settings)
    
    # 에러 핸들러 설정
    async def on_error(context: TurnContext, error: Exception):
        print(f"Error occurred: {error}")
        await context.send_activity("죄송합니다. 오류가 발생했습니다.")
    
    adapter.on_turn_error = on_error
    
    return adapter


# 봇 인스턴스 생성
BOT = EchoBot()
ADAPTER = create_adapter()


async def messages(req: Request) -> Response:
    """
    메시지 엔드포인트 핸들러
    """
    # Content-Type 확인
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
    else:
        return Response(status=415, text="Unsupported Media Type")
    
    # Activity 역직렬화
    try:
        activity = Activity().deserialize(body)
    except Exception as e:
        print(f"Failed to deserialize activity: {e}")
        return Response(status=400, text="Bad Request")
    
    # Authorization 헤더 가져오기
    auth_header = req.headers.get("Authorization", "")
    
    try:
        # 봇 처리
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=201)
        
    except Exception as e:
        print(f"Error processing activity: {e}")
        return Response(status=500, text="Internal Server Error")


def init_func(argv):
    """
    Azure Functions용 초기화 함수
    """
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    return app


if __name__ == "__main__":
    """
    로컬 개발용 서버 실행
    """
    try:
        # 환경 변수 확인
        app_id="ef49f037-efa3-4680-a649-c78e26c6c673",
        app_password="0Sf8Q~9g9C33VDMkOJxA7562Wqu-FbMcT3Y19cs-"
        
        if not app_id or not app_password:
            print("Warning: MICROSOFT_APP_ID 또는 MICROSOFT_APP_PASSWORD가 설정되지 않았습니다.")
            print("Bot Framework Emulator에서는 이 값들이 비어있어도 됩니다.")
        
        # 웹 애플리케이션 생성
        app = web.Application()
        app.router.add_post("/api/messages", messages)
        
        # 서버 시작
        port = int(os.environ.get("PORT", 3978))
        print(f"봇이 포트 {port}에서 실행중입니다.")
        print(f"Bot Framework Emulator에서 http://localhost:{port}/api/messages 로 연결하세요.")
        
        web.run_app(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        print(f"서버 시작 오류: {e}")
        raise e