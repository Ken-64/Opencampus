import os
from openai import OpenAI


def bot_response(client, user_input,conversation_history=[]):
    conversation_history.append({"role": "user", "content": user_input})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    conversation_history.append({"role": "assistant", "content": response})
    return response, conversation_history


if __name__ == '__main__':
    client = OpenAI(
        api_key='sk-proj-FxWWRvSKKJIBL3pvHTvuT3BlbkFJdoJBDfFdsw0wKTABA5M9',
    )
    conversation_history = []
    response, conversation_history = bot_response(client,
                       'The client contacted us because he is looking for the interested club in the University. '
                       'You should act as a friendly assistant and ask questions in japanese to clearly understand the '
                       'interested area of users. You know the user is interested in a specific area, but you need to figure out '
                       'what it is. Ask one question at a time and be friendly. Your job is to gather information. Do not create '
                       'information. Information must be provided by the client. Ask only what-questions and avoid confirmation questions. Ask more dichotomous questions.Avoid using self-identifying prefixes in your response,'
                       ' such as "Assistant:". The whole process requires more than 3 questions. If you think you have gathered enough information to determine that the user is interested in a'
                       ' specific area of interest, such as "Basketball" or "Football" rather than the general'
                       ' "Sports", respond: “完全に理解しました。xxxに興味がありますね。”', conversation_history)
    while True:
        answer = input(response)
        response, conversation_history = bot_response(client, answer, conversation_history)
