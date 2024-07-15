import os
import pandas as pd
import csv
import json
from openai import OpenAI


def initialization():
    client = OpenAI(
        api_key='sk-proj-FxWWRvSKKJIBL3pvHTvuT3BlbkFJdoJBDfFdsw0wKTABA5M9',
    )
    genre_list = get_genre_list(file_path)
    initial_prompt = ('The client contacted us because he is looking for the interested club in the University. '
                      'You should act as a friendly assistant and ask questions in only japanese to clearly understand the '
                      'interested area of users based on the list. You know the user is interested in a specific area, but you need to figure out '
                      'what it is. You should aim to discover one hobby rather than multiple ones. Your questions should ask for details about the users hobbies and try to get the user to express their opinions. '
                      'Ask one question at a time and be friendly. Please prioritize responding to the  question using what '
                      'or which over the confirmation question. For example, focus more on answering questions that ask for details '
                      'or specifics rather than simply confirming interest. Ask more dichotomous questions. Avoid showing all the genres to user. Avoid a too long question. Avoid using self-identifying prefixes in your response,'
                      ' such as "Assistant:".')
    first_question = ('興味のある分野はありますか？スポーツ、文学、芸術など。')

    genre_prompt = ('The above is the requirement of a student for a university club. '
                    'You should select the 3 most relevant genres from the club genre list I will give below. '
                    'Do not reply with any extra content, just reply with the name of the genre. Split them by "@".'
                    '\nClub Genre List: ' + str(genre_list))

    return client, initial_prompt, first_question, genre_prompt


def transform_json(path):
    json_file_path = '../データ/データ7.15.json'
    df = pd.read_csv(path)
    df.replace("", float("NaN"), inplace=True)
    df.dropna(how='all', inplace=True)
    json_result = df.to_json(orient='records', force_ascii=False)
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_result)
    return json_file_path


def get_clubs_info(clubs, club_list):
    club_info = []
    for tar_club in clubs:
        for club in club_list:
            if club['サークル'] == tar_club:
                club_info.append(club)
    return club_info


def get_genre_list(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    column_values = list(dict.fromkeys(entry['ラベル２'] for entry in data if entry['ラベル２'] is not None))
    return column_values


def description_chat(client, clubs_info, conversation_history):
    club_prompt = ('The above is the requirement of a student for a university club. '
                   'You should use natural words to describe clubs and explain why they are suitable for the user based on the club information I will give below. '
                   '\nClub Information: ' + str(clubs_info))
    conversation_history.append({"role": "system", "content": club_prompt})
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[-1].message.content
    conversation_history.pop()
    return response


def club_chat(client, club_list, conversation_history):
    club_prompt = ('The above is the requirement of a student for a university club. '
                   'You should select the 3 most relevant clubs from the club list I will give below. '
                   'Do not reply with any extra content, just reply with the name of the club. Split them by "@" '
                   '\nClub List: ' + str(club_list))
    conversation_history.append({"role": "system", "content": club_prompt})
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


def get_club_list(genre, path):
    club_list = []
    seen_items = set()
    genres = genre.split("@")
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

        for genre in genres:
            for item in data:
                if item['ラベル２'] == genre:
                    item_tuple = tuple(item.items())
                    if item_tuple not in seen_items:
                        seen_items.add(item_tuple)
                        club_list.append(item)
    return club_list


if __name__ == '__main__':
    file_path = transform_json("../データ/データ7.15.csv")
    client, initial_prompt, first_question, genre_prompt = initialization()
    conversation_history = []

    user_answer = input(first_question)
    conversation_history.append({"role": "system", "content": initial_prompt})
    conversation_history.append({"role": "assistant", "content": first_question})
    model_response, conversation_history = opening_chat(client, user_answer, conversation_history)
    for _ in range(4):
        user_answer = input(model_response)
        model_response, conversation_history = opening_chat(client, user_answer, conversation_history)
    conversation_history.pop(0)

    genre = genre_chat(client, genre_prompt, conversation_history)
    club_list = get_club_list(genre, file_path)
    clubs = club_chat(client, club_list, conversation_history).split("@")
    clubs_info = get_clubs_info(clubs, club_list)
    print(description_chat(client, clubs_info, conversation_history))
