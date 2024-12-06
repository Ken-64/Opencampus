import pandas as pd
import streamlit as st
import json
from openai import OpenAI



def initialization():
    client = OpenAI(
        api_key='',
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
                    'You should select the 1-3 most relevant genres from the club genre list I will give below. '
                    'Do not reply with any extra content, just reply with the name of the genre. Split them by "@".'
                    '\nClub Genre List: ' + str(genre_list))
    conversation_history = []
    conversation_history.append({"role": "system", "content": initial_prompt})
    conversation_history.append({"role": "assistant", "content": first_question})

    return client, conversation_history, first_question, genre_prompt


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
            if club['サークル'] == tar_club or club['サークル'] == f'{tar_club}\n':
                club_info.append(club)
    return club_info


def get_genre_list(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    column_values = list(dict.fromkeys(entry['ラベル２'] for entry in data if entry['ラベル２'] is not None))
    return column_values


def description_chat(client, clubs_info, conversation_history):
    club_prompt = ('The above is the requirement of a student for a university club. And I will give one club below'
                   'You should describe the selected club and explain why they are suitable. Note that you should use japanese.'
                   'Note that it should be less than 150 words in one paragraph. Note that you should use natural words. '
                   'Avoid using sentence like "選ばれたクラブは「xxx」です"'
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


def opening_chat(client, prompt, conversation_history):
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

def initialize_session(conversation_history):
    """Initialize the Streamlit session state."""
    if 'step' not in st.session_state:
        st.session_state.conversation_history = conversation_history
        st.session_state.step = 0

def render_greeting(image_path, greeting):
    """Render the greeting message."""
    st.markdown(f"""
        <div style="display: flex; align-items: center;"> 
            <img src="{image_path}" style="width: 25px; margin-right: 10px;" />
            <div style="font-size: 16px;">{greeting}</div>
        </div>
    """, unsafe_allow_html=True)

def handle_user_input(client, step_key):
    """Handle user input and update the conversation."""
    user_answer = st.text_input("答え:", key=f"input_{step_key}")
    if st.button("提出する", key=f"submit_{step_key}"):
        st.session_state.model_response, st.session_state.conversation_history = opening_chat(client, user_answer,
                                                                                              st.session_state.conversation_history)
        st.session_state.step += 1
        st.rerun()
    else:
        st.stop()

def render_conversation(conversation_history, image_path1, image_path2):
    """Render the conversation history."""
    for conversation in conversation_history:
        reply = conversation['content']
        if conversation['role'] == 'assistant':
            st.markdown(f"""
                <div style="display: flex; align-items: center;"> 
                    <img src="{image_path1}" style="width: 25px; margin-right: 10px;" />
                    <div style="font-size: 16px;">{reply}</div>
                </div>
            """, unsafe_allow_html=True)
        elif conversation['role'] == 'user':
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; align-items: center;"> 
                    <div style="font-size: 16px;">{reply}</div>
                    <span style="display: inline-block; width: 10px;"></span>
                    <img src="{image_path2}" style="width: 20px; margin-right: 10px;" />
                </div>
            """, unsafe_allow_html=True)

def process_final_step(client, genre_prompt, file_path):
    """Handle the final step in the chat interaction."""
    genre = genre_chat(client, genre_prompt, st.session_state.conversation_history)
    club_list = get_club_list(genre, file_path)
    clubs = club_chat(client, club_list, st.session_state.conversation_history).split("@")
    clubs_info = get_clubs_info(clubs, club_list)
    descriptions = []
    for each_club in clubs_info:
        descriptions.append(description_chat(client, each_club, st.session_state.conversation_history))
    for each_description in descriptions:
        for club in clubs:
            each_description = each_description.replace(club, f"<span style='font-size:20px;'>**{club}**</span>")
        st.markdown(each_description + "\n", unsafe_allow_html=True)




if __name__ == '__main__':
    file_path = transform_json("../データ/データ7.15.csv")
    client, conversation_history, first_question, genre_prompt = initialization()
    st.title("LLMに聞いてみよう。あなたにお勧めのサークルは！？")
    image_path1 = 'https://i.imgur.com/MNQoZSK.jpg'
    image_path2 = 'https://i.imgur.com/o6oe2ra.png'

    initialize_session(conversation_history)

    if st.session_state.step == 3:
        st.session_state.conversation_history.pop(0)
        st.session_state.conversation_history.pop()

    greeting = "こんにちは！僕はサークル活動をおすすめするチャットボット、クラブボットだよ！🎉<br><br>大学生活は勉強だけじゃなくて、クラブ活動も大" \
               "事だよね。君がスポーツ好きでも、アートが得意でも、技術オタクでも、ピッタリのクラブを見つけるお手伝いをするよ！<br><br>さあ、この楽しいテストを始めよう。まず最初に教えてね——<br><br>"

    render_greeting(image_path1, greeting)
    render_conversation(st.session_state.conversation_history, image_path1, image_path2)

    if st.session_state.step == 0:
        handle_user_input(client, st.session_state.step)
    elif st.session_state.step < 3:
        handle_user_input(client, st.session_state.step)
    elif st.session_state.step == 3:
        process_final_step(client, genre_prompt, file_path)