# Career Conversation

An AI-powered conversational assistant that represents your professional profile on the web. Visitors can chat with an assistant that answers questions about your background, experience, and skills using your own summary and resume content.

The app runs a Gradio-based chat UI backed by an OpenAI-compatible LLM (configured to call Gemini via a custom base URL). It also supports tool calls to capture user interest and log unknown questions, sending you real-time notifications.


## Features
- AI chat about your career profile
  - Uses a structured system prompt built from your details in `self_information.Me` (name, summary, resume snippet)
  - Initial assistant greeting is pre-seeded and appears in the chat history
  - Stays in character and is optimized for professional, helpful responses
- Tool calling
  - Capture leads (asks for email and records it)
  - Log any question the assistant couldn’t answer
  - Sends notifications via NotificationAPI (email/SMS depending on your config)
- Simple, modern chat UI
  - Gradio ChatInterface with `type="messages"` (OpenAI-style role/content format)
  - Dark mode enabled via a JS hook
  - Custom browser tab title set to “Career Conversation”
- Response quality guardrails
  - Built-in checks validate assistant replies and can trigger a controlled rerun with feedback


## Prerequisites
- Python 3.10+ recommended (tested with Python 3.12)
- A modern browser (Chrome, Edge, Safari, Firefox)
- API keys and credentials (see Configuration)


## Quick Start
1) Clone the repo
- ```bash
  git clone https://github.com/Kaushik-Paul/Career-Conversation.git
  ```
- ```bash
  cd Career-Conversation
  ```

2) Create and activate a virtual environment
- ```bash
  python3 -m venv .venv
  ```
- ```bash
  source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
  ```

3) Install uv
  - Linux/macOS:
    - ```bash
      curl -LsSf https://astral.sh/uv/install.sh | less
      ```
    - Ensure ~/.local/bin is on your PATH (restart shell or run):
    - ```bash
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
      ```
  - Windows (PowerShell):
    - ```bash
      powershell -c "irm https://astral.sh/uv/install.ps1 | more"
      ```


4) Install dependencies
```bash
uv sync
```

5) Create a .env file
Create a `.env` file in the project root with the following variables (adjust as needed):
- `GOOGLE_API_KEY=your_gemini_or_provider_key`
- `DEEPSEEK_API_KEY=optional_if_used`
- `GROQ_API_KEY=optional_if_used`

# NotificationAPI (for email/SMS notifications)
`NOTIFICATION_USER=your_notificationapi_user`
`NOTIFICATION_TOKEN=your_notificationapi_token`
`NOTIFICATION_EMAIL=your_destination_email@example.com`
`NOTIFICATION_NUMBER=+1XXXXXXXXXX`

6) Configure model and endpoint
Open `main/constants.py` and verify:
- `GEMINI_BASE_URL` points to your OpenAI-compatible endpoint for Gemini
- gemini_model is set to the desired model name

7) Add your resume and summary resources
- Place your resume PDF at `resources/kaushik-paul-resume.pdf`
- Place your summary text at `resources/summary.txt`
- If you use different filenames/paths, update them in `main/self_information.py` accordingly.

Example:
```bash
mkdir -p resources
cp /path/to/your_resume.pdf resources/kaushik-paul-resume.pdf
echo "A short 3–5 sentence professional summary about you." > resources/summary.txt
```

8) Customize your profile
Open `main/self_information.py` and update `Me` with your:
- name
- summary
- resume profile snippet

9) Run the app
- python main/app.py

Gradio will print a local URL (e.g., http://127.0.0.1:7860). Open it in your browser.


## Usage Notes
- First message
  - The assistant greets users with a pre-seeded message that is included in the chat history.
- Data formats
  - The chat components use `type="messages"` (role/content dicts). If you change this, keep the UI and backend consistent.
- Tools / Notifications
  - When the assistant triggers lead capture or unknown-question logging, the app sends a notification via NotificationAPI using your `.env` credentials.
- Theming & Tab Title
  - The JS hook sets dark mode and the page title to “Career Conversation”. Adjust in `Chatbot.__init__` if you want a different theme or title.


## Troubleshooting
- ValueError or format errors about chatbot messages
  - Ensure both `gr.Chatbot(..., type="messages")` and `gr.ChatInterface(..., type="messages")` are set, and that messages are dicts with `role` and `content` keys.
- No notifications received
  - Double-check NotificationAPI credentials in `.env` and their validity. Ensure destination email/number is correct.
- Model or API errors
  - Confirm your `GEMINI_BASE_URL` and `gemini_model` in `constants.py` and that your `GOOGLE_API_KEY` is valid for that endpoint.
- Virtualenv issues on Windows
  - Use `.venv\\Scripts\\activate` and ensure `python` maps to the interpreter inside the venv.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
