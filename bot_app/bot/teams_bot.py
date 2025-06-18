from botbuilder.schema import OAuthCard,HeroCard, CardAction, Attachment, ActivityTypes, Activity, ActionTypes
from botbuilder.core import MessageFactory, TurnContext, CardFactory
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.core.teams import TeamsInfo
from handler.summary_handler import handle_summary_request
from util.token_helper import get_token, save_conversation_reference
from dotenv import load_dotenv
import os
    
load_dotenv()

domain = os.getenv("DOMAIN")

class TeamsMailBot(TeamsActivityHandler):

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:

            if member.id != turn_context.activity.recipient.id:

                await turn_context.send_activity(
                    MessageFactory.attachment(self._create_suggested_action_card())
                )

    def _create_suggested_action_card(self) -> Attachment:
        card = HeroCard(
            title="Mail Assistant",
            text="무엇을 도와드릴까요?",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="오늘 메일 요약하기", value="요약"),
                CardAction(type=ActionTypes.im_back, title="메일 검색하기", value="검색"),
            ],
        )
        return CardFactory.hero_card(card)
        
    async def on_message_activity(self, turn_context: TurnContext):
        
        user_id = turn_context.activity.from_property.id
        access_token = get_token(user_id)
        
        if not access_token:
            ref = TurnContext.get_conversation_reference(turn_context.activity)
            save_conversation_reference(user_id, ref)

            login_url = f"{domain}/auth/login?user_id={user_id}"
            
            # 사용자가 로그인하지 않은 경우, 로그인 링크 제공
            await turn_context.send_activity(
                f"🔐 먼저 로그인 해주세요: [로그인 링크]({login_url})"
            )
            return

        # 로그인 완료 됐으면, 일반 메시지 처리 로직 시작
        print("access_token:", access_token)

        # 사용자 input에 따라 분기처리 
        user_input = turn_context.activity.text.strip().lower()

        if "요약" in user_input:
            # 요약 요청 처리
            await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
            
            await handle_summary_request(turn_context, access_token)


        elif "검색" in user_input:  
            # 검색 요청 처리
            await turn_context.send_activity("🔍 메일을 검색해드릴게요. 검색어를 입력해주세요.")
