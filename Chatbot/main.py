import os
import pandas as pd
import csv
import json
from openai import OpenAI


def upload_file_once(client, file_path):
    message_file = client.files.create(
        file=open(file_path, "rb"), purpose="assistants"
    )
    file_id_data = {"file_id": message_file.id}
    with open("../データ/file_id.json", "w") as f:
        json.dump(file_id_data, f)


def search_clubs(client,conversation_history):
    my_assistant = client.beta.assistants.create(
        description='The client contacted us because he is looking for the interested club in the University.',
        instructions='You should search for and pick up at least 3 clubs that are suitable for users based on the requirements provided by users,'
                     'like the areas of interest and specific preferences. Then provide detailed information in Japanese.'
                     'Notice that do not show the source ID',
        name="Club Recommending Tutor",
        tools=[{"type": "file_search"}],
        model="gpt-3.5-turbo",
    )

    vector_store = client.beta.vector_stores.create(name="Club data")

    assistant = client.beta.assistants.update(
        assistant_id=my_assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    with open("../データ/file_id.json", "r") as f:
        file_id_data = json.load(f)
    file_id = file_id_data["file_id"]

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": str(conversation_history),
                "attachments": [
                    {"file_id": file_id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    return message_content.value


def bot_response(client, user_input, conversation_history=[]):
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

    # upload_file_once(client, '../データ/サークルデータ.json')
    conversation_history = []
    initial_prompt = ('The client contacted us because he is looking for the interested club in the University. '
                      'You should act as a friendly assistant and ask questions in only japanese to clearly understand the '
                      'interested area of users. You know the user is interested in a specific area, but you need to figure out '
                      'what it is. Ask one question at a time and be friendly. Your job is to gather information. Do not create '
                      'information. Information must be provided by the client. Ask only what-questions and avoid confirmation questions. Ask more dichotomous questions.Avoid using self-identifying prefixes in your response,'
                      ' such as "Assistant:". The whole process requires more than 5 questions. If you think you have gathered enough information to determine that the user is interested in a'
                      ' specific area of interest, such as "Basketball" or "Football" rather than the general'
                      ' "Sports", respond: “完全に理解しました。xxxに興味がありますね。”')
    model_response, conversation_history = bot_response(client, initial_prompt, conversation_history)
    while "完全に理解しました" not in model_response:
        user_answer = input(model_response)
        model_response, conversation_history = bot_response(client, user_answer, conversation_history)
    conversation_history.pop(0)
    print(search_clubs(client,conversation_history))
