from botbuilder.schema import HeroCard, CardAction, Attachment, ActivityTypes, Activity, ActionTypes
from botbuilder.core import MessageFactory, TurnContext, CardFactory
from botbuilder.core.teams import TeamsActivityHandler
from handler.summary_handler import handle_summary_request
from core.mail_uploader import get_mail_status
from util.token_helper import get_token, save_conversation_reference
from dotenv import load_dotenv
import os
from core.mail_fetcher import fetch_all_mails
from util.graph_helper import get_user_principal_name
from handler.search_handler import handle_search_request
from util.llm_helper import generate_response
    
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
        # 사용자가 메시지를 보낼 때마다 Typing 애니메이션 표시
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

        user_id = turn_context.activity.from_property.id
        access_token = get_token(user_id)
        
        if not access_token:
            ref = TurnContext.get_conversation_reference(turn_context.activity)
            save_conversation_reference(user_id, ref)

            login_url = f"{domain}/auth/login?user_id={user_id}"
            
            # 사용자가 로그인하지 않은 경우, 로그인 링크 제공
            await turn_context.send_activity(
                f"🔐 본인 확인을 위해 먼저 로그인 해주세요: [로그인 링크]({login_url})"
            )
            return

        user_email = get_user_principal_name(access_token)

        status = get_mail_status(user_email)
        
        print(f"📧 현재 메일 상태: {status} (user_id: {user_email})")

        # 상태에 따라 다른 메시지 전송
        if status == "not_found":
            await turn_context.send_activity("🔄 메일 수집을 시작합니다. 잠시만 기다려주세요.")

            await turn_context.send_activity(Activity(type=ActivityTypes.typing))

            await fetch_all_mails(access_token)

            await turn_context.send_activity("✅ 메일 수집이 완료되었습니다. 다시 질문해주세요.")
            
        elif status == "pending":
            await turn_context.send_activity("🔄 현재 백드라운드로 메일 수집 중입니다. 나중에 다시 말 걸어주세요.")
            
            return
        
        elif status == "error":
            await turn_context.send_activity("❗ 메일 수집 중 오류가 발생했습니다. 관리자에게 문의해주세요.")
            return

        else:

            # 사용자 input에 따라 분기처리 
            user_input = turn_context.activity.text.strip().lower()

            intent = generate_response("", user_input)

            if intent == "summary":
                # 요약 요청 처리
                await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")

                await turn_context.send_activity(Activity(type=ActivityTypes.typing))
                
                await handle_summary_request(turn_context, access_token)

            elif intent == "search":
                # 검색 요청 처리
                await turn_context.send_activity("📬 입력하신 내용 기반으로 관련된 메일 찾아드릴게요. 잠시만 기다려주세요.")

                # 검색 로직 추가 필요
                await turn_context.send_activity(Activity(type=ActivityTypes.typing))

                await handle_search_request(turn_context, user_input)

            else:
                await turn_context.send_activity("🤖 메일 요약 또는 검색 요청이 아닌 것 같아요. 어떤 작업을 도와드릴까요?")

                




    