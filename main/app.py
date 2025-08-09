# imports
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import gradio as gr
import asyncio
from notificationapi_python_server_sdk import notificationapi

import constants
from self_information import Me
from evaluation import ChatEvaluation

# load environment variables
load_dotenv(override=True)

google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

# initialize notificationapi
# To send notifications to my email
notificationapi.init(
  os.getenv("NOTIFICATION_USER"),
  os.getenv("NOTIFICATION_TOKEN")
)


async def push_notification(message):
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


def record_user_details(email, name="not provided", notes="not provided"):
    asyncio.run(push_notification(f"Recording interest from \nName: {name} , \nEmail: {email} , \nNotes: {notes}"))
    return {"recorded": "ok"}


def record_unknown_question(question):
    asyncio.run(push_notification(f"Recording question that was asked but I couldn't answer \nQuestion: {question}"))
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}


record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if tool_name == "record_user_details":
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)

        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results


class Chatbot:
    def __init__(self):
        self.gemini = OpenAI(api_key=google_api_key, base_url=constants.GEMINI_BASE_URL)
        me = Me()
        name = me.name
        summary = me.summary
        resume = me.resume

        self.tools = [{"type": "function", "function": record_user_details_json},
                      {"type": "function", "function": record_unknown_question_json}]

        self.system_prompt = self.fetch_system_prompt(name, summary, resume)

        # First message that will be displayed
        initial_messages = [
            {
                "role": "assistant",
                "content": f"Hello there! Welcome to my professional website. \
                I'm {name}, and it's a pleasure to connect with you. How can I assist you today, \
                or perhaps tell you more about my experience and skills?"
            }
        ]

        chat_ui = gr.Chatbot(value=initial_messages, type="messages")

        custom_js = "() => { document.title = 'Career Conversation'; document.body.classList.add('dark'); }"
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/chatbot.png"))
        gr.ChatInterface(self.chat, chatbot=chat_ui, type="messages", js=custom_js).launch(favicon_path=icon_path)

    def fetch_system_prompt(self, name, summary, resume):
        system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
        particularly questions related to {name}'s career, background, skills and experience. \
        Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
        You are given a summary of {name}'s background and Resume of {name} which you can use to answer questions. \
        Be professional and engaging, as if talking to a potential client or future employer who came across the resume. \
        If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{summary}\n\n## Resume Profile:\n{resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

        return system_prompt

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": message}]
        done = False
        evaluate_response = ChatEvaluation()
        while not done:

            # This is the call to the LLM - see that we pass in the tools json

            response = self.gemini.chat.completions.create(model=constants.gemini_model, messages=messages, tools=self.tools)

            finish_reason = response.choices[0].finish_reason
            reply = response.choices[0].message.content

            # If the LLM wants to call a tool, we do that!
            if finish_reason == "tool_calls":
                res = response.choices[0].message
                tool_calls = res.tool_calls
                results = handle_tool_calls(tool_calls)
                messages.append(res)
                messages.extend(results)
            else:
                # Check the response of the LLM
                evaluation = evaluate_response.evaluate(reply, message, history)

                if evaluation.is_acceptable:
                    done = True
                else:
                    reply = evaluate_response.rerun(self.system_prompt, reply, message, history, evaluation.feedback)
                    done = True

        return reply


if __name__ == "__main__":
    chatbot = Chatbot()
