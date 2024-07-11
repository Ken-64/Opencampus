import os
from openai import OpenAI


def bot_response(client, user_input,conversation_history=[]):
    conversation_history.append({"role": "user", "content": user_input})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    return response, conversation_history


if __name__ == '__main__':
    client = OpenAI(
        api_key='sk-proj-FxWWRvSKKJIBL3pvHTvuT3BlbkFJdoJBDfFdsw0wKTABA5M9',
    )
    conversation_history = []
    response, conversation_history = bot_response(client,
                       'クライアントは、大学で好きなクラブに入りたいために私たちに連絡してきました。'
                       'あなたは、ユーザーがどの分野に興味を持っているかを明確に把握する責任を持つ'
                       'フレンドリーなエージェントとして行動し、質問する必要があります。ユーザーが何'
                       'かに興味を持っていることはわかっていますが、それが何であったかを知る必要があ'
                       'るため、あなたはそれを見つけ出す必要があります。一度に 1 つの質問だけをし、フ'
                       'レンドリーにしてください。あなたの仕事はサポートを提供することではなく、情報'
                       'を収集することだけです。情報を作成してはいけません。情報はクライアントから提供'
                       'される必要があります。返信には「Agent:」などの自己識別プレフィックスを使用しな'
                       'いでください。', conversation_history)
    while True:
        answer = input(response)
        response, conversation_history = bot_response(client, answer, conversation_history)
