import telebot

# Инициализация бота
TOKEN = '8159160029:AAFqOA0ec8ZlCkZgYBUIjbZ_jA2K007AqdA'
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('tasks.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_name TEXT,
    description TEXT,
    due_date TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    reminder_time TEXT
)
''')
conn.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    add_task_button = types.InlineKeyboardButton("Добавить задачу", callback_data='add_task')
    set_reminder_button = types.InlineKeyboardButton("Установить напоминание", callback_data='set_reminder')
    view_tasks_button = types.InlineKeyboardButton("Просмотреть задачи", callback_data='view_tasks')
    markup.add(add_task_button, set_reminder_button, view_tasks_button)

    bot.send_message(message.chat.id, 'Привет! Я ваш ежедневник. Выберите действие:', reply_markup=markup)

# Обработчик для добавления задачи
@bot.callback_query_handler(func=lambda call: call.data == 'add_task')
def add_task_button(call):
    bot.send_message(call.message.chat.id, 'Введите название задачи и описание через пробел:')
    bot.register_next_step_handler(call.message, process_add_task)

# Обработчик для установки напоминания
@bot.callback_query_handler(func=lambda call: call.data == 'set_reminder')
def set_reminder_button(call):
    bot.send_message(call.message.chat.id, 'Введите ID задачи и время напоминания (в формате HH:MM):')
    bot.register_next_step_handler(call.message, process_set_reminder)

# Обработчик для просмотра задач
@bot.callback_query_handler(func=lambda call: call.data == 'view_tasks')
def view_tasks_button(call):
    user_id = call.message.chat.id
    tasks = cursor.execute('SELECT id, task_name, description, due_date FROM tasks WHERE user_id = ?', (user_id,)).fetchall()

    if tasks:
        task_list = "\n".join([f"{task[0]}. {task[1]}: {task[2]} (Дата: {task[3]})" for task in tasks])
        bot.send_message(call.message.chat.id, f'Ваши задачи:\n{task_list}')
    else:
        bot.send_message(call.message.chat.id, 'У вас нет задач.')

# Обработчик ввода данных для задачи
def process_add_task(message):
    user_id = message.from_user.id
    task_name = message.text.split()[0]
    description = ' '.join(message.text.split()[1:])
    due_date = '2023-12-31'  # Пример даты

    cursor.execute('INSERT INTO tasks (user_id, task_name, description, due_date) VALUES (?, ?, ?, ?)',
                   (user_id, task_name, description, due_date))
    conn.commit()

    bot.send_message(message.chat.id, 'Задача добавлена!')

# Обработчик ввода данных для напоминания
def process_set_reminder(message):
    task_id, reminder_time = message.text.split()

    cursor.execute('INSERT INTO reminders (task_id, reminder_time) VALUES (?, ?)',
                   (task_id, reminder_time))
    conn.commit()

    bot.send_message(message.chat.id, 'Напоминание установлено!')

# Функция для отправки напоминаний
def send_reminders():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Планировщик задач
def schedule_reminders():
    reminders = cursor.execute('SELECT task_id, reminder_time FROM reminders').fetchall()
    for reminder in reminders:
        task_id, reminder_time = reminder
        schedule.every().day.at(reminder_time).do(send_reminder, task_id)

def send_reminder(task_id):
    task = cursor.execute('SELECT user_id, task_name FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task:
        user_id, task_name = task
        bot.send_message(user_id, f'Напоминание: {task_name}')

# Запуск планировщика в отдельном потоке
reminder_thread = threading.Thread(target=send_reminders)
reminder_thread.start()

# Запуск планировщика
schedule_reminders()

# Запуск бота
bot.polling()
