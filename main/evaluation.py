import os
from dotenv import load_dotenv
from pydantic import BaseModel
from groq import Groq
import instructor
from openai import OpenAI

from system_prompt import EvaluationPrompt
import constants

load_dotenv(override=True)

groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

groq_client = Groq(
    api_key=groq_api_key
)

class ChatEvaluation:
    def __init__(self):
        self.evaluator_system_prompt = EvaluationPrompt().fetch_evaluator_system_prompt()
        self.groq_client = instructor.from_provider("groq/llama-3.3-70b-versatile")
        self.gemini = OpenAI(api_key=google_api_key, base_url=constants.GEMINI_BASE_URL)

    def evaluate(self, reply, message, history) -> Evaluation:
        messages = [{"role": "system", "content": self.evaluator_system_prompt}] + [{"role": "user", "content": EvaluationPrompt.evaluator_user_prompt(reply, message, history)}]
        response = self.groq_client.chat.completions.create(messages=messages, response_model=Evaluation)
        return response

    def rerun(self, system_prompt, reply, message, history, feedback):
        updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
        response = self.gemini.chat.completions.create(model=constants.gemini_model, messages=messages)
        return response.choices[0].message.content
