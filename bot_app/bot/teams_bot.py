from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, CardFactory
from botbuilder.schema import CardAction, ActionTypes, HeroCard, Attachment

class TeamsMailBot(ActivityHandler):
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.attachment(self._create_suggested_action_card())
                )

    def _create_suggested_action_card(self) -> Attachment:
        card = HeroCard(
            title="Outlook Assistant",
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
            await turn_context.send_activity("오늘 받은 메일을 요약해드릴게요.")
            # 👉 여기에 메일 요약 함수 호출 (예: summarize_today_mails(user_id))
        elif "검색" in user_input:
            await turn_context.send_activity("검색할 메일 키워드를 입력해주세요.")
        else:
            await turn_context.send_activity("죄송해요, 이해하지 못했어요. '요약' 또는 '검색'을 입력해보세요.")
