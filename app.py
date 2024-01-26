from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def generate_response(prompt, role="user"):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            # 賦予他角色
            {"role": "system", "content": "你是一個很厲害的高級軟體工程師，精通正體中文和英文，根本是一個超專業的助理"},
            # user給prompt
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    bot_response = generate_response(user_message)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bot_response)
    )

if __name__ == "__main__":
    app.run(debug=True)