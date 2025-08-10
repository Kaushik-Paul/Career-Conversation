import asyncio
from dotenv import load_dotenv
import os
from notificationapi_python_server_sdk import notificationapi

load_dotenv(override=True)


class NotificationAPI:
    def __init__(self):
        # initialize notificationapi
        # To send notifications to my email
        notificationapi.init(
            os.getenv("NOTIFICATION_USER"),
            os.getenv("NOTIFICATION_TOKEN")
        )

    async def push_notification(self, message):
        response = await notificationapi.send({
            "type": "ai_agents_notification",
            "to": {
                "number": os.getenv("NOTIFICATION_NUMBER"),
                "email": os.getenv("NOTIFICATION_EMAIL")
            },
            "parameters": {
                "comment": message
            }
        })

    def record_user_details(self, email, name="not provided", notes="not provided"):
        asyncio.run(self.push_notification(f"Recording interest from \nName: {name}, \nEmail: {email}, \nNotes: {notes}"))
        return {"recorded": "ok"}

    def record_unknown_question(self, question):
        asyncio.run(
            self.push_notification(f"Recording question that was asked but I couldn't answer. \nQuestion: {question}"))
        return {"recorded": "ok"}

