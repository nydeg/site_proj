import sqlite3
import telebot
from telebot import types
import datetime as dt
import threading

bot = telebot.TeleBot('5830879893:AAGDZTLWWZwzzRkSFpWfUbTfYbL9TWHQehI')

plans = {}
tg_LOG = False


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Да')
    item2 = types.KeyboardButton('Нет')

    markup.add(item1, item2)

    global plans
    plans = {}

    bot.send_message(message.chat.id, 'Здравствуй, {0.first_name}!\nЯ телеграм-бот, '
                                      'который поможет вам не забывать о планах\nВы '
                                      'уже зарегистрировались на сайте?'.format(message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type == 'private':
        chat_id = message.chat.id
        global tg_LOG
        if message.text == '✅ Добавить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.register_next_step_handler(message, add_plan)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            if tg_LOG:
                item3 = types.KeyboardButton('Выйти из аккаунта')
            else:
                item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, 'Введите название плана', reply_markup=markup)

        elif message.text == 'Да':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Да!')
            item2 = types.KeyboardButton('Пожалуй, не сейчас')
            markup.add(item1, item2)

            bot.send_message(chat_id, 'Хотите войти в аккаунт?', reply_markup=markup)

        elif message.text == 'Да!':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.register_next_step_handler(message, tg_login)
            item1 = types.KeyboardButton('Пожалуй, не сейчас')
            markup.add(item1)

            bot.send_message(chat_id, 'Введите почту, с которой вы зарегистрировались', reply_markup=markup)

        elif message.text == 'Нет':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Хочу!')
            item2 = types.KeyboardButton('Пожалуй, не сейчас')
            markup.add(item1, item2)

            bot.send_message(chat_id, 'Хотите создать аккаунт?', reply_markup=markup)

        elif message.text == 'Хочу!':
            # тут надо прописать инлайн кнопку с ссылкой на сайт после хоста
            pass

        elif message.text == 'Войти в аккаунт':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.register_next_step_handler(message, tg_login)
            item1 = types.KeyboardButton('Пожалуй, не сейчас')
            markup.add(item1)

            bot.send_message(chat_id, 'Введите почту, с которой вы зарегистрировались', reply_markup=markup)

        elif message.text == 'Выйти из аккаунта':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tg_LOG = False
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            item3 = types.KeyboardButton('Войти в аккаунт')
            s = []
            for i in range(0, len(plans[chat_id]) - 1, 2):
                if plans[chat_id][i + 1] != '':
                    s.append(plans[chat_id][i])
                    s.append(plans[chat_id][i + 1])
            plans[chat_id] = s

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, 'Чтобы ознакомиться, перейдите в 📚 Информация',
                             reply_markup=markup)

        elif message.text == 'Пожалуй, не сейчас':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, 'Чтобы ознакомиться, перейдите в 📚 Информация',
                             reply_markup=markup)

        elif message.text == '✉ Мои планы':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if tg_LOG:
                update_plans(chat_id)
            if chat_id not in plans or not plans[chat_id]:
                item1 = types.KeyboardButton('✅ Добавить')
                item2 = types.KeyboardButton('❌ Удалить')
                item3 = types.KeyboardButton('🤔 Когда напоминание?')
                back = types.KeyboardButton('⬅ Назад')
                markup.add(item1, item2, item3, back)

                bot.send_message(chat_id, 'У вас нет планов', reply_markup=markup)

            else:
                h = ''
                for i, plan in enumerate(plans[chat_id][::2], start=1):
                    h += str(i) + '. '
                    h += plan
                    h += '\n'
                item1 = types.KeyboardButton('✅ Добавить')
                item2 = types.KeyboardButton('❌ Удалить')
                item3 = types.KeyboardButton('🤔 Когда напоминание?')
                back = types.KeyboardButton('⬅ Назад')
                markup.add(item1, item2, item3, back)

                bot.send_message(chat_id, h, reply_markup=markup)

        elif message.text == '📚 Информация':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('📖 Описание бота')
            item2 = types.KeyboardButton('❓ Как пользоваться?')
            back = types.KeyboardButton('⬅ Назад')
            markup.add(item1, item2, back)

            bot.send_message(chat_id, 'Что именно вам интересно узнать?', reply_markup=markup)

        elif message.text == '⬅ Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            if tg_LOG:
                item3 = types.KeyboardButton('Выйти из аккаунта')
            else:
                item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, '⬅ Назад', reply_markup=markup)

        elif message.text == '❓ Как пользоваться?':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.send_message(message.chat.id, 'Добавьте план и поочередно, следуя указаниям, введите:\nНазвание '
                                              'плана\nДату и время напоминания в формате ДД.ММ.ГГГГ ЧЧ:ММ')
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            if tg_LOG:
                item3 = types.KeyboardButton('Выйти из аккаунта')
            else:
                item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, 'Пример ввода:\nУборка\n16.08.2023 10:30', reply_markup=markup)

        elif message.text == '📖 Описание бота':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            if tg_LOG:
                item3 = types.KeyboardButton('Выйти из аккаунта')
            else:
                item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)

            bot.send_message(chat_id, 'Этот бот представлет собой удобные заметки\nВ него вы '
                                      'можете записывать свои планы, и он обязательно напомнит вам о них\nТакже '
                                      'данного бота '
                                      'можно использовать как напоминалку, если не хотите забыть о бытовых '
                                      'делах', reply_markup=markup)

        elif message.text == '❌ Удалить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if tg_LOG:
                update_plans(chat_id)
            if chat_id not in plans or not plans[chat_id]:
                item1 = types.KeyboardButton('✉ Мои планы')
                item2 = types.KeyboardButton('📚 Информация')
                if tg_LOG:
                    item3 = types.KeyboardButton('Выйти из аккаунта')
                else:
                    item3 = types.KeyboardButton('Войти в аккаунт')
                markup.add(item1, item2, item3)

                bot.send_message(chat_id, 'У вас нет планов', reply_markup=markup)

            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                bot.register_next_step_handler(message, delete_plan)
                item1 = types.KeyboardButton('✉ Мои планы')
                item2 = types.KeyboardButton('📚 Информация')
                if tg_LOG:
                    item3 = types.KeyboardButton('Выйти из аккаунта')
                else:
                    item3 = types.KeyboardButton('Войти в аккаунт')

                markup.add(item1, item2, item3)

                bot.send_message(chat_id, 'Какой план вы хотите отменить? (Напишите)', reply_markup=markup)

        elif message.text == '🤔 Когда напоминание?':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            if tg_LOG:
                update_plans(chat_id)
                item3 = types.KeyboardButton('Выйти из аккаунта')
            else:
                item3 = types.KeyboardButton('Войти в аккаунт')

            markup.add(item1, item2, item3)
            if chat_id not in plans or not plans[chat_id]:
                bot.send_message(message.chat.id, 'Сначала добавьте план', reply_markup=markup)

            else:
                bot.send_message(message.chat.id, 'Время напоминания какого плана вы хотите узнать? (Напишите)',
                                 reply_markup=markup)
                bot.register_next_step_handler(message, nap)


def tg_login(message):
    chat_id = message.chat.id
    email = message.text
    con = sqlite3.connect('db/blogs.db')
    cur = con.cursor()
    reg = cur.execute("""SELECT email from users""").fetchall()
    reg = [i[0] for i in reg]
    con.close()
    if email in reg:
        bot.send_message(chat_id, 'Введите пароль')
        bot.register_next_step_handler(message, tg_password, email)
    elif email == 'Пожалуй, не сейчас':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('✉ Мои планы')
        item2 = types.KeyboardButton('📚 Информация')
        item3 = types.KeyboardButton('Войти в аккаунт')
        markup.add(item1, item2, item3)
        bot.send_message(chat_id, "Вы не вошли в аккаунт", reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Нет пользователя с такой почтой. Попробуйте еще раз')
        bot.register_next_step_handler(message, tg_login)


def tg_password(message, email):
    chat_id = message.chat.id
    password = message.text
    with open('pass.txt', 'r', encoding='utf8') as f:
        text = f.readline().split()
        curr_password = text[0]
        curr_email = text[1]
    if password == curr_password:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('✉ Мои планы')
        item2 = types.KeyboardButton('📚 Информация')
        item3 = types.KeyboardButton('Выйти из аккаунта')
        markup.add(item1, item2, item3)
        con = sqlite3.connect('db/blogs.db')
        cur = con.cursor()
        result = cur.execute("""SELECT title FROM jobs
                        WHERE connection=(SELECT id from users WHERE email = ?)""", (email, )).fetchall()
        cur.execute("""UPDATE users
                    SET tg_id = ?
                    WHERE email = ?""", (chat_id, curr_email))
        con.commit()
        lst = []
        for i in result:
            lst.append(i[0])
            lst.append('')
        con.close()
        if chat_id not in plans:
            plans[chat_id] = lst
        else:
            plans[chat_id] = lst + plans[chat_id]
        global tg_LOG
        tg_LOG = True
        bot.send_message(chat_id, "Вы вошли в аккаунт", reply_markup=markup)
    elif password == 'Пожалуй, не сейчас':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('✉ Мои планы')
        item2 = types.KeyboardButton('📚 Информация')
        item3 = types.KeyboardButton('Войти в аккаунт')
        markup.add(item1, item2, item3)
        bot.send_message(chat_id, "Вы не вошли в аккаунт", reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Вы ввели неправильный пароль или не вошли в аккаунт на сайте. Попробуйте еще раз')
        bot.register_next_step_handler(message, tg_password, email)


def add_plan(message):
    chat_id = message.chat.id
    plan = message.text

    if chat_id not in plans:
        plans[chat_id] = [plan]
    else:
        plans[chat_id].append(plan)

    bot.send_message(message.chat.id, "Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ")
    bot.register_next_step_handler(message, add_to_list)


def add_to_list(message):
    chat_id = message.chat.id
    date_name = message.text
    days = ['31', '28', '31', '30', '31', '30', '31', '31', '30', '31', '30', '31']
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    if len(date_name) == 16 and date_name[2] == '.' and date_name[5] == '.' and date_name[10] == ' '\
            and date_name[-3] == ':' and date_name[3:5].isdigit() and date_name[0:2].isdigit()\
            and date_name[6:10].isdigit() and date_name[11:13].isdigit() and date_name[14:].isdigit()\
            and int(date_name[6:10]) >= 2023 and date_name[3:5] in months:
        k = months.index(date_name[3:5])
        max_days = int(days[k])
        if date_name[3:5] == '02' and int(date_name[6:10]) % 4 == 0:
            max_days += 1
        if 0 < int(date_name[:2]) <= max_days and 0 <= int(date_name[11:13]) < 24 and 0 <= int(
                date_name[14:]) < 60:
            plans[chat_id].append(date_name)
            if tg_LOG:
                con = sqlite3.connect('db/blogs.db')
                cur = con.cursor()
                numb = len(cur.execute("""SELECT title from jobs""").fetchall()) + 1
                connection = int(cur.execute("""SELECT id from users WHERE tg_id = ?""", (chat_id, )).fetchone()[0])
                cur.execute("""INSERT INTO jobs VALUES(?, ?, ?, ?, ?)""", (numb, connection, plans[chat_id][-2],
                                                                           False, plans[chat_id][-1]))
                con.commit()
                con.close()
            bot.send_message(chat_id, "План добавлен")
        else:
            bot.send_message(chat_id, 'Некорректный ввод. Попробуйте еще раз')
            bot.register_next_step_handler(message, add_to_list)
    else:
        bot.send_message(chat_id, 'Некорректный ввод. Попробуйте еще раз')
        bot.register_next_step_handler(message, add_to_list)


def delete_plan(message):
    chat_id = message.chat.id
    del_plan = message.text
    global tg_LOG
    if del_plan in plans[chat_id]:
        n = plans[chat_id].index(del_plan)
        if tg_LOG:
            con = sqlite3.connect('db/blogs.db')
            cur = con.cursor()
            cur.execute("""DELETE FROM jobs
                        WHERE connection=(SELECT id from users WHERE tg_id = ?) AND
                        title = ? AND date = ?""", (chat_id, del_plan, plans[chat_id][n + 1]))
            con.commit()
            con.close()
        plans[chat_id].remove(del_plan)
        plans[chat_id].remove(plans[chat_id][n])
        bot.send_message(chat_id, 'План успешно удален!')
    else:
        bot.send_message(chat_id, 'Такого плана нет')


def nap(message):
    chat_id = message.chat.id
    mes_to_save = message.text

    if mes_to_save in plans[chat_id]:
        x = plans[chat_id].index(mes_to_save)
        if plans[chat_id][x + 1] != '':
            bot.send_message(message.chat.id,
                             f'Напоминание о плане {plans[chat_id][x]} придет {plans[chat_id][x + 1][:10]} числа'
                             f' в {plans[chat_id][x + 1][11:]}')
        else:
            bot.send_message(message.chat.id, 'На этот план не установлено время напоминания')
    else:
        bot.send_message(message.chat.id, 'Такого плана нет')


def update_plans(chat_id):
    con = sqlite3.connect('db/blogs.db')
    cur = con.cursor()
    new_plans = cur.execute("""SELECT title, date FROM jobs
                            WHERE connection=(SELECT id from users WHERE tg_id = ?)""", (chat_id,)).fetchall()
    lst = []
    for x in new_plans:
        lst.append(x[0])
        if x[1] is None:
            lst.append('')
        else:
            lst.append(x[1])
    plans[chat_id] = lst
    con.close()


def check_plans():
    current_time = dt.datetime.now()
    global tg_LOG
    for z in list(plans.keys()):
        for plan in plans[z][::2]:
            n = plans[z].index(plan)
            if len(plans[z]) - 1 > n:
                if plans[z][n + 1] != '':
                    date_time_obj = dt.datetime.strptime(plans[z][n + 1], '%d.%m.%Y %H:%M')
                    if current_time > date_time_obj:
                        bot.send_message(z, f"Время для плана {plan} наступило.\nСкорее выполните его!")
                        if tg_LOG:
                            con = sqlite3.connect('db/blogs.db')
                            cur = con.cursor()
                            cur.execute("""DELETE FROM jobs
                                WHERE connection=(SELECT id from users WHERE tg_id = ?) AND title = ?
                                AND date = ?""", (z, plan, plans[z][n + 1]))
                            planss = cur.execute("""SELECT title from jobs""").fetchall()
                            planss = [i[0] for i in planss]
                            length = len(planss)
                            if length > 0:
                                for my_id in range(1, length + 1):
                                    cur.execute("""UPDATE jobs
                                                SET id = ?
                                                WHERE title = ?""", (my_id, planss[my_id - 1]))
                            con.commit()
                            con.close()

                        plans[z].remove(plan)
                        plans[z].remove(plans[z][n])

    threading.Timer(15, check_plans).start()


def bot_func():
    check_plans()
    bot.polling()
