# imports
from dotenv import load_dotenv
from openai import OpenAI
import os
import gradio as gr
import time

import constants
from self_information import Me
from evaluation import ChatEvaluation
from system_prompt import ChatPrompt
from tool_functions import ToolFunction

# load environment variables
load_dotenv(override=True)

google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')


class Chatbot:
    def __init__(self):
        self.gemini = OpenAI(api_key=google_api_key, base_url=constants.GEMINI_BASE_URL)
        me = Me()
        name = me.name

        self.system_prompt = ChatPrompt().system_prompt

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

    def simulate_typing(self, text, chunk_size=3, delay=0.02):
        """Simulate typing effect by yielding chunks of text."""

        for i in range(0, len(text), chunk_size):
            yield text[:i + chunk_size]
            time.sleep(delay)

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": message}]
        done = False
        evaluate_response = ChatEvaluation()
        
        while not done:
            response = self.gemini.chat.completions.create(
                model=constants.gemini_model,
                messages=messages,
                tools=ToolFunction.get_tools_list()
            )

            finish_reason = response.choices[0].finish_reason
            reply = response.choices[0].message.content

            # If the LLM wants to call a tool, we do that!
            if finish_reason == "tool_calls":
                res = response.choices[0].message
                tool_calls = res.tool_calls
                results = ToolFunction.handle_tool_calls(tool_calls)
                messages.append(res)
                messages.extend(results)
            else:
                # Evaluate the complete response first
                evaluation = evaluate_response.evaluate(reply, message, history)

                if evaluation.is_acceptable:
                    for chunk in self.simulate_typing(reply):
                        yield chunk
                    done = True
                else:
                    # Get the improved response
                    reply = evaluate_response.rerun(
                        self.system_prompt, 
                        reply, 
                        message, 
                        history, 
                        evaluation.feedback
                    )
                    for chunk in self.simulate_typing(reply):
                        yield chunk
                    done = True


if __name__ == "__main__":
    chatbot = Chatbot()
