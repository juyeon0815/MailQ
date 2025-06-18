from botbuilder.schema import OAuthCard,HeroCard, CardAction, Attachment, ActivityTypes, Activity, ActionTypes
from botbuilder.core import MessageFactory, TurnContext, CardFactory
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.core.teams import TeamsInfo
from handler.summary_handler import handle_summary_request

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
        adapter = turn_context.adapter

        token_response = await adapter.get_user_token(turn_context, connection_name="SSO")

        if token_response and token_response.token:
            access_token = token_response.token
            await turn_context.send_activity("✅ 로그인 성공! access_token 발급 완료")
            # 👉 여기서 access_token 사용해 Graph API 호출 가능
        else:
            # ❗ access_token이 없으면 로그인 카드 전송
            await self._send_login_card(turn_context)

        # 사용자가 메시지 입력할 때 마다 멤버 조회 필수
        try:
            # Teams 컨텍스트에서 멤버 정보 가져오기
            member = await TeamsInfo.get_member(
                turn_context, 
                turn_context.activity.from_property.id
            )

            if not member:
                await turn_context.send_activity("🚨 해당 봇을 사용할 수 없는 사용자 입니다. 관리자에게 문의해주세요.")
                return
            
            user_email = getattr(member, 'email', None)
            print(f"User Email: {user_email}")  # 디버깅용 출력

            # 사용자 input에 따라 분기처리 
            user_input = turn_context.activity.text.strip().lower()

            if "요약" in user_input:
                # 요약 요청 처리
                await turn_context.send_activity("📬 오늘 받은 메일을 요약해드릴게요.")
                
                await handle_summary_request(turn_context)


            elif "검색" in user_input:  
                # 검색 요청 처리
                await turn_context.send_activity("🔍 메일을 검색해드릴게요. 검색어를 입력해주세요.")
                
                
        except Exception as e:
            await turn_context.send_activity("🚨 해당 봇을 사용할 수 없는 사용자 입니다. 관리자에게 문의해주세요.")

    async def _send_login_card(self, turn_context: TurnContext):
        oauth_card = OAuthCard(
            text="Outlook에 로그인해주세요",
            connection_name="teams-oauth",  # SSO 연결 이름
            buttons=[
                CardAction(
                    type=ActionTypes.signin,
                    title="로그인",
                    value=""
                )
            ]
        )

        attachment = Attachment(
            content_type="application/vnd.microsoft.card.oauth",  # ✅ 여기!
            content=oauth_card
        )

        activity = Activity(
            type=ActivityTypes.message,
            attachments=[attachment]
        )

        await turn_context.send_activity(activity)