import os
import pandas as pd
import csv
import json
from openai import OpenAI


def initialization():
    client = OpenAI(
        api_key='sk-proj-FxWWRvSKKJIBL3pvHTvuT3BlbkFJdoJBDfFdsw0wKTABA5M9',
    )
    file_path = "../データ/サークルデータ.json"
    genre1_list = get_genre_list(1, file_path)
    genre2_list = get_genre_list(2, file_path)
    initial_prompt = ('The client contacted us because he is looking for the interested club in the University. '
                      'You should act as a friendly assistant and ask questions in only japanese to clearly understand the '
                      'interested area of users based on the list. You know the user is interested in a specific area, but you need to figure out '
                      'what it is. You should aim to discover one hobby rather than multiple ones. Your questions should ask for details about the users hobbies and try to get the user to express their opinions. '
                      'Ask one question at a time and be friendly. Please prioritize responding to the  question using what '
                      'or which over the confirmation question. For example, focus more on answering questions that ask for details '
                      'or specifics rather than simply confirming interest. Ask more dichotomous questions. Avoid showing all the genres to user. Avoid a too long question. Avoid using self-identifying prefixes in your response,'
                      ' such as "Assistant:".')
    first_question = ('興味のある分野はありますか？スポーツ、文学、芸術など。')
    genre1_prompt = ('The above is the requirement of a student for a university club. '
                     'You should select the 2 most relevant genres from the club genre list I will give below. '
                     'Do not reply with any extra content, just reply with the name of the genre. '
                     '\nClub Genre List: ' + str(genre1_list))
    genre2_prompt = ('The above is the requirement of a student for a university club. '
                     'You should select the 3 most relevant genres from the club genre list I will give below. '
                     'Do not reply with any extra content, just reply with the name of the genre. '
                     '\nClub Genre List: ' + str(genre2_list))

    return client, file_path, initial_prompt, first_question, genre1_prompt, genre2_prompt


def get_genre_list(genre_key, path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if genre_key == 2:
        column_values = list(dict.fromkeys(entry['ラベル２'] for entry in data if entry['ラベル２'] is not None))
    else:
        column_values = list(dict.fromkeys(entry['ラベル1'] for entry in data if entry['ラベル1'] is not None))
    return column_values


def club_chat(client, club_list, conversation_history):
    conversation_history.append({"role": "system", "content": prompt})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    conversation_history.pop()
    return response


def genre_chat(client, prompt, conversation_history):
    conversation_history.append({"role": "system", "content": prompt})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    conversation_history.pop()
    return response


def opening_chat(client, prompt, conversation_history=[]):
    conversation_history.append({"role": "user", "content": prompt})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    conversation_history.append({"role": "assistant", "content": response})
    return response, conversation_history


def get_club_list(genre1, genre2, path):
    club_list = []
    seen_items = set()
    genre1 = genre1.split("、")
    genre2 = genre2.split("、")
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for genre in genre1:
            for item in data:
                if item['ラベル1'] == genre:
                    item_tuple = tuple(item.items())
                    if item_tuple not in seen_items:
                        seen_items.add(item_tuple)
                        club_list.append(item)
        for genre in genre2:
            for item in data:
                if item['ラベル２'] == genre:
                    item_tuple = tuple(item.items())
                    if item_tuple not in seen_items:
                        seen_items.add(item_tuple)
                        club_list.append(item)
    return club_list


if __name__ == '__main__':
    client, file_path, initial_prompt, first_question, genre1_prompt, genre2_prompt = initialization()
    conversation_history = []

    user_answer = input(first_question)
    conversation_history.append({"role": "system", "content": initial_prompt})
    conversation_history.append({"role": "assistant", "content": first_question})
    model_response, conversation_history = opening_chat(client, user_answer, conversation_history)
    for _ in range(4):
        user_answer = input(model_response)
        model_response, conversation_history = opening_chat(client, user_answer, conversation_history)
    conversation_history.pop(0)

    genre1 = genre_chat(client, genre1_prompt, conversation_history)
    genre2 = genre_chat(client, genre2_prompt, conversation_history)
    club_list = get_club_list(genre1, genre2, file_path)
