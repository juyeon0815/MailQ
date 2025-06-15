from botbuilder.core import TurnContext
from botbuilder.schema import ActivityTypes

class MyBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            await turn_context.send_activity(f"Echo: {turn_context.activity.text}")