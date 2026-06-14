import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ExpenseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.expense_id = self.scope["url_route"]["kwargs"]["expense_id"]
        self.room_group_name = f"expense_{self.expense_id}"
        self.user = self.scope.get("user")

        if self.user is None or not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send last 50 comments on connect
        history = await self.get_comment_history()
        await self.send(text_data=json.dumps({"type": "chat.history", "messages": history}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "chat.message":
            text = data.get("text", "").strip()
            if not text:
                return
            comment = await self.save_comment(text)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": comment,
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type": "chat.message", "message": event["message"]}))

    @database_sync_to_async
    def save_comment(self, text):
        from .models import ExpenseComment
        from api.expenses.models import Expense

        expense = Expense.objects.get(id=self.expense_id)
        comment = ExpenseComment.objects.create(
            expense=expense, user=self.user, text=text
        )
        return {
            "id": str(comment.id),
            "user": {"id": str(self.user.id), "name": self.user.name, "email": self.user.email},
            "text": comment.text,
            "created_at": comment.created_at.isoformat(),
        }

    @database_sync_to_async
    def get_comment_history(self):
        from .models import ExpenseComment

        comments = (
            ExpenseComment.objects.filter(expense_id=self.expense_id)
            .select_related("user")
            .order_by("-created_at")[:50]
        )
        return [
            {
                "id": str(c.id),
                "user": {"id": str(c.user.id), "name": c.user.name, "email": c.user.email},
                "text": c.text,
                "created_at": c.created_at.isoformat(),
            }
            for c in reversed(list(comments))
        ]
