import telebot
import datetime
import time
import threading
import random
from telebot import types

bot = telebot.TeleBot('8159160029:AAFqOA0ec8ZlCkZgYBUIjbZ_jA2K007AqdA')

# Множество для хранения отправленных сообщений (чтобы избежать дублирования)
send_messages = set()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    user_name = message.from_user.first_name
    # Создаем клавиатуру с кнопкой "Получить мотивашку"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    fact_button = types.KeyboardButton("Получить мотивашку")
    markup.add(fact_button)

    # Отправляем приветственное сообщение с кнопкой
    bot.reply_to(message, f'Привет, {user_name}! Я чат-бот, который будет напоминать тебе, что можно жить лучше!',
                 reply_markup=markup)

    # Запуск потока для напоминаний

    def send_reminders(chat_id):
        first_rem = "08:30"
        second_rem = "12:00"
        end_rem = "21:40"

        with open("motivaxa.txt", encoding="utf-8") as file:
            list1 = [line.strip() for line in file if line.strip()]

        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == first_rem:
                random_fact1 = random.choice(list1)
                while random_fact1 in send_messages:
                    random_fact = random.choice(list1)
                bot.send_message(chat_id, text=f"{user_name}, {random_fact1}")
                send_messages.add(random_fact1)
                time.sleep(61)
                continue
            if now == second_rem:
                random_fact1 = random.choice(list1)
                while random_fact1 in send_messages:
                    random_fact = random.choice(list1)
                bot.send_message(chat_id, text=f"{user_name}, {random_fact1}")
                send_messages.add(random_fact1)
                time.sleep(61)
                continue
            if now == end_rem:
                random_fact1 = random.choice(list1)
                while random_fact1 in send_messages:
                    random_fact = random.choice(list1)
                bot.send_message(chat_id, text=f"{user_name}, {random_fact1}")
                send_messages.add(random_fact1)
                time.sleep(61)
                continue
            time.sleep(1)

    reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,))
    reminder_thread.start()

@bot.message_handler(func=lambda message: message.text == "Старт")
def start_bot(message):
    user_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    fact_button = types.KeyboardButton("Получить мотивашку")
    markup.add(fact_button)
    bot.send_message(message.chat.id, "Бот запущен!", reply_markup=markup)
    bot.send_message(message.chat.id, "Выберите действие:")


@bot.message_handler(commands=['fact'])
def fact_message(message):
    user_name = message.from_user.first_name
    # Создаем кнопку получить мотивашку
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    fact_button = types.KeyboardButton("Получить мотивашку")
    markup.add(fact_button)
    with open("motivaxa.txt", encoding="utf-8") as file:
        list = [line.strip() for line in file if line.strip()]
        random_fact = random.choice(list)
        bot.reply_to(message, f'{user_name} , {random_fact}', reply_markup=markup)
        send_messages.add(random_fact)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Получить мотивашку":
        fact_message(message)






if __name__ == "__main__":
    bot.polling(none_stop=True)