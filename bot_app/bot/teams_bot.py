from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, CardFactory
from botbuilder.schema import CardAction, ActionTypes, HeroCard, Attachment
from util.llm_helper import generate_response
import os
from dotenv import load_dotenv
from handler.summary_handler import handle_summary_request
from core.mail_uploader import check_user_exists, get_mail_status
from core.mail_fetcher import fetch_today_mails, fetch_all_mails
import asyncio

load_dotenv()

class TeamsMailBot(ActivityHandler):
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:

                access_token = os.getenv("ACCESS_TOKEN")
                print(access_token)
                status = get_mail_status("juyeon@dev0815.onmicrosoft.com")

                if status == "pending":
                    await turn_context.send_activity("⏳ 메일을 수집 중입니다. 잠시만 기다려주세요.")
                    return
                
                elif status == "done":
                    await turn_context.send_activity("📬 수집이 완료되어 Agent를 시작합니다.")
                    
                    await turn_context.send_activity(
                    MessageFactory.attachment(self._create_suggested_action_card())
                    )
                    
                else:
                    await turn_context.send_activity("📦 메일을 수집하고 있어요. 잠시만 기다려주세요.")
                    asyncio.create_task(fetch_all_mails(access_token))
                    
                    await turn_context.send_activity("✅ 메일 수집이 완료되었습니다.")
                    
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
        
        print("🔔 [on_message_activity] 메세지 수신됨.")
        
        try:
            
            user_input = turn_context.activity.text.strip().lower()
            print(f"Received user input: {user_input}")

            if "요약" in user_input:

                await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
                await handle_summary_request(turn_context)

                # await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
                # await handle_summary_request(turn_context)

            elif "검색" in user_input:
                print("User requested search.")
                # await turn_context.send_activity("검색할 메일 키워드를 입력해주세요.")

            else:
                print("LLM 응답 생성 중...")
                response = await generate_response("",user_input)
                print(f"LLM 응답: {response}")
                await turn_context.send_activity(response)
                # await turn_context.send_activity("죄송해요, 이해하지 못했어요. '요약' 또는 '검색'을 입력해보세요.")

        except Exception as e:
            print("🔥 [on_message_activity] 오류 발생:", e)
            # await turn_context.send_activity("❌ 내부 오류가 발생했습니다.")


    # async def on_message_activity(self, turn_context: TurnContext):
    #     user_input = turn_context.activity.text.strip().lower()

    #     print(f"Received user input: {user_input}")

    #     if "요약" in user_input:

    #         print("User requested summary.")

    #         await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
            
    #         await handle_summary_request(turn_context)
    #         # try :
    #         #     # 사용자 ID를 가져옵니다.
    #         #     accss_token = os.getenv("ACCESS_TOKEN")

    #         #     user_id = get_user_principal_name(accss_token)  # 사용자 ID를 가져오는 함수 호출
    #         #     print(f"사용자 ID: {user_id}")

    #         #     # DB에 사용자 정보가 없다면 메일 일어오고, 보관함 + 아카이브 메일 백업 필요

    #         #     # 사용자 메일을 가져옵니다.
    #         #     mails = get_user_mails(user_id)  # 사용자 메일을 가져오는 함수 호출

    #         #     # 👉 여기에 메일 요약 함수 호출 (예: summarize_today_mails(user_id))
    #         #     await turn_context.send_activity("메일 요약을 처리 중입니다...")
    #         #     result = summarize_emails(mails)  # 이 부분은 실제 메일 요약 함수로 대체해야 합니다.
    #         #     await turn_context.send_activity(f"오늘의 메일 요약: {result}")
    #         #     # 예시: result = summarize_today_mails(user_id)
    #         #     # await turn_context.send_activity(f"오늘의 메일 요약: {result}")
            
    #         # except Exception as e:
    #         #     await turn_context.send_activity(f"오류가 발생했습니다: {str(e)}")

    #         # 👉 여기에 메일 요약 함수 호출 (예: summarize_today_mails(user_id))
    #     elif "검색" in user_input:
    #         print("User requested search.")
    #         await turn_context.send_activity("검색할 메일 키워드를 입력해주세요.")
    #         # 검색 기능 구현
    #         # 만약 DB에 데이터가 없다면 메일함 + 아카이브 백업 필요
    #     else:
    #         print("User input not recognized, sending default response.")
    #         await turn_context.send_activity("죄송해요, 이해하지 못했어요. '요약' 또는 '검색'을 입력해보세요.")