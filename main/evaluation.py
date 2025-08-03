import os
from dotenv import load_dotenv
from pydantic import BaseModel
from groq import Groq
import instructor
from openai import OpenAI

from self_information import Me
import constants

load_dotenv(override=True)

groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


def fetch_evaluator_system_prompt(name, summary, resume):
    evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
    You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
    The Agent is playing the role of {name} and is representing {name} on their website. \
    The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
    The Agent has been provided with context on {name} in the form of their summary and Resume details. Here's the information:"

    evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## Resume:\n{resume}\n\n"
    evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

    return evaluator_system_prompt


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


groq_client = Groq(
    api_key=groq_api_key
)

class ChatEvaluation:
    def __init__(self):
        me = Me()
        self.name = me.name
        self.summary = me.summary
        self.resume = me.resume
        self.evaluator_system_prompt = fetch_evaluator_system_prompt(self.name, self.summary, self.resume)
        self.groq_client = instructor.from_provider("groq/llama-3.3-70b-versatile")
        self.gemini = OpenAI(api_key=google_api_key, base_url=constants.GEMINI_BASE_URL)

    def evaluate(self, reply, message, history) -> Evaluation:
        messages = [{"role": "system", "content": self.evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
        response = self.groq_client.chat.completions.create(messages=messages, response_model=Evaluation)
        return response


    def rerun(self, system_prompt, reply, message, history, feedback):
        updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
        response = self.gemini.chat.completions.create(model=constants.gemini_model, messages=messages)
        return response.choices[0].message.content
