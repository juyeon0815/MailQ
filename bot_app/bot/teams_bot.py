from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, CardFactory
from botbuilder.schema import CardAction, ActionTypes, HeroCard, Attachment
from util.llm_helper import generate_response
import os
from dotenv import load_dotenv
from handler.summary_handler import handle_summary_request


load_dotenv()

class TeamsMailBot(ActivityHandler):
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
        user_input = turn_context.activity.text.strip().lower()

        if "요약" in user_input:
            await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
            
            await handle_summary_request(turn_context)
            # try :
            #     # 사용자 ID를 가져옵니다.
            #     accss_token = os.getenv("ACCESS_TOKEN")

            #     user_id = get_user_principal_name(accss_token)  # 사용자 ID를 가져오는 함수 호출
            #     print(f"사용자 ID: {user_id}")

            #     # DB에 사용자 정보가 없다면 메일 일어오고, 보관함 + 아카이브 메일 백업 필요

            #     # 사용자 메일을 가져옵니다.
            #     mails = get_user_mails(user_id)  # 사용자 메일을 가져오는 함수 호출

            #     # 👉 여기에 메일 요약 함수 호출 (예: summarize_today_mails(user_id))
            #     await turn_context.send_activity("메일 요약을 처리 중입니다...")
            #     result = summarize_emails(mails)  # 이 부분은 실제 메일 요약 함수로 대체해야 합니다.
            #     await turn_context.send_activity(f"오늘의 메일 요약: {result}")
            #     # 예시: result = summarize_today_mails(user_id)
            #     # await turn_context.send_activity(f"오늘의 메일 요약: {result}")
            
            # except Exception as e:
            #     await turn_context.send_activity(f"오류가 발생했습니다: {str(e)}")

            # 👉 여기에 메일 요약 함수 호출 (예: summarize_today_mails(user_id))
        elif "검색" in user_input:
            await turn_context.send_activity("검색할 메일 키워드를 입력해주세요.")
            # 검색 기능 구현
            # 만약 DB에 데이터가 없다면 메일함 + 아카이브 백업 필요
        else:
            # await turn_context.send_activity("죄송해요, 이해하지 못했어요. '요약' 또는 '검색'을 입력해보세요.")
             # ✨ LLM 응답 처리 (예: GPT 기반 답변)
            await turn_context.send_activity("질문 내용을 이해하고 있어요. 답변을 생성 중입니다...")
            response = generate_response(user_input)
            await turn_context.send_activity(response)