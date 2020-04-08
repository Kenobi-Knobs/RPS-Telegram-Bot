import telebot
import requests
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

token = "YOUR TOKEN"
print(token)

bot = telebot.TeleBot(token)
wait_time = 60# /10
games = {}
markup = InlineKeyboardMarkup()
markup.add(InlineKeyboardButton("🤜", callback_data="rock"),InlineKeyboardButton("✌️", callback_data="scissor"),InlineKeyboardButton("✋", callback_data="paper"))


class Game:
    mess_id = None
    chat_id = None
    wait_time = None
    count = 0
    user = [None,None]

    def __init__(self, mess_id, chat_id, wait_time):
        self.count = 0
        self.user = [None,None]
        self.mess_id = mess_id
        self.wait_time = wait_time

    def add_user(self, user_id, user_name ,user_hand):
        if self.count <= 1:
            self.user[self.count] = str(user_id) +"|"+str(user_name)+"|"+str(user_hand)
            self.count += 1

def refresh_message(mess_id, chat_id):
    try:
        player1 = "?"
        player2 = "?"
        if games[str(mess_id) + str(chat_id)].user[0] != None:
            player1 = games[str(mess_id) + str(chat_id)].user[0].split("|")[1]
        if games[str(mess_id) + str(chat_id)].user[1] != None:
            player2 = games[str(mess_id) + str(chat_id)].user[1].split("|")[1]
        bot.edit_message_text(chat_id=chat_id, message_id=mess_id, text=" Ожидаю игроков...\n " + player1 + " VS "+ player2 +" \n Осталось: "+ str(games[str(mess_id) + str(chat_id)].wait_time) +"с \n Чтобы присоединится выбери что-то", reply_markup=markup)
    except:
        return 0

def delete_game(mess_id, chat_id):
    try:
        games[str(mess_id) + str(chat_id)].user[0] = None
        games[str(mess_id) + str(chat_id)].user[1] = None
        del games[str(mess_id) + str(chat_id)]
        bot.delete_message(chat_id=chat_id, message_id=mess_id)
    except:
        return 0

def wait_game(mess_id, chat_id):
    try:
        while games[str(mess_id) + str(chat_id)].wait_time > 0:
            time.sleep(10)
            games[str(mess_id) + str(chat_id)].wait_time -=10;
            refresh_message(mess_id, chat_id)
        delete_game(mess_id, chat_id)
    except:
        return 0

def start_game(mess_id, chat_id, wait_time):
    games[str(mess_id) + str(chat_id)] = Game(mess_id, chat_id, wait_time)
    wait_thread = threading.Thread(target=wait_game, args=(mess_id,chat_id,))
    wait_thread.start()

def emoji(str):
    if str == "rock":
        return "🤜"
    if str == "scissor":
        return "✌️"
    if str == "paper":
        return "✋"

def show_win(mess_id, chat_id, text):
    try:
        games[str(mess_id) + str(chat_id)].user[0] = None
        games[str(mess_id) + str(chat_id)].user[1] = None
        del games[str(mess_id) + str(chat_id)]
        bot.edit_message_text(chat_id=chat_id, message_id=mess_id, text=text)
    except:
        bot.send_message(chat_id,text)
        return 0

def check_winner(mess_id, chat_id):
    player1 = games[str(mess_id) + str(chat_id)].user[0].split("|")
    player2 = games[str(mess_id) + str(chat_id)].user[1].split("|")

    if player1[2] == player2[2]:
        show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nНичья")
    else:
        if player1[2] == "rock" and player2[2] == "scissor":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player1[1])
        if player2[2] == "rock" and player1[2] == "scissor":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player2[1])

        if player1[2] == "scissor" and player2[2] == "paper":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player1[1])
        if player2[2] == "scissor" and player1[2] == "paper":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player2[1])

        if player1[2] == "paper" and player2[2] == "rock":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player1[1])
        if player2[2] == "paper" and player1[2] == "rock":
            show_win(mess_id,chat_id, player1[1] + emoji(player1[2]) + " \n     VS\n " + player2[1] + emoji(player2[2]) +"\n\nПобедил(а): " + player2[1])

@bot.message_handler(commands=['rps_game'])
def rps_game_comm(message):
    global wait_time
    if message.chat.type != "private":
        mess = bot.reply_to(message, " Ожидаю игроков...\n ? VS ? \n Осталось: "+ str(wait_time) +"с \n Чтобы присоединится выбери что-то",reply_markup=markup)
        start_game(mess.message_id, mess.chat.id, wait_time)


@bot.callback_query_handler(func=lambda c:True)
def inline(c):
    hand = c.data
    mess_id = c.message.message_id
    chat_id = c.message.chat.id
    user_id = c.from_user.id
    last_name = ""

    if c.from_user.last_name != None:
        last_name =  c.from_user.last_name

    user_name = str(c.from_user.first_name) + " " + last_name
    user_name.strip()


    curent_users_id = []
    for player in  games[str(mess_id) + str(chat_id)].user:
        if player != None:
            curent_users_id.append(str(player).split("|")[0])

    if str(user_id) in curent_users_id:
        bot.answer_callback_query(c.id, text="Ты уже в игре")
    else:
        if games[str(mess_id) + str(chat_id)].user[0] == None or games[str(mess_id) + str(chat_id)].user[1] == None:
            games[str(mess_id) + str(chat_id)].add_user(user_id, user_name, hand)
            bot.answer_callback_query(c.id, text="Ты выбрал " + emoji(hand))
            refresh_message(mess_id, chat_id)
            if games[str(mess_id) + str(chat_id)].count > 1 :
                check_winner(mess_id, chat_id)
        else:
            bot.answer_callback_query(c.id, text="Ты лишний :(")

bot.polling(none_stop=True, interval=0)
