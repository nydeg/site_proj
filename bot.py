import telebot
from telebot import types
import datetime as dt
import threading


bot = telebot.TeleBot(TOKEN)

plans = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('✉ Мои планы')
    item2 = types.KeyboardButton('📚 Информация')

    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Здравствуй, {0.first_name}!\nЯ телеграм-бот, '
                                      'который поможет вам не забывать о планах\nЧтобы '
                                      'узнать больше перейдите в 📚 Информация.\nЕсли хотите '
                                      'воспользоваться, то перейдите в ✉ Мои планы'.format(message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type == 'private':
        chat_id = message.chat.id
        if message.text == '✅ Добавить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.register_next_step_handler(message, add_plan)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')

            markup.add(item1, item2)

            bot.send_message(chat_id, 'Введите название плана', reply_markup=markup)

        elif message.text == '✉ Мои планы':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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

            markup.add(item1, item2)

            bot.send_message(chat_id, '⬅ Назад', reply_markup=markup)

        elif message.text == '❓ Как пользоваться?':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.send_message(message.chat.id, 'Добавьте план и поочередно, следуя указаниям, введите:\nНазвание '
                                              'плана\nДату и время напоминания в формате ДД.ММ.ГГГГ ЧЧ:ММ')
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')

            markup.add(item1, item2)

            bot.send_message(chat_id, 'Пример ввода:\nУборка\n16.08.2023 10:30', reply_markup=markup)

        elif message.text == '📖 Описание бота':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')

            markup.add(item1, item2)

            bot.send_message(chat_id, 'Этот бот представлет собой удобные заметки\nВ него вы '
                                      'можете записывать свои планы и он обязательно напомнит вам о них\nТакже '
                                      'данного бота '
                                      'можно использовать как напоминалку, если не хотите забыть о бытовых '
                                      'делах', reply_markup=markup)

        elif message.text == '❌ Удалить':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if chat_id not in plans or not plans[chat_id]:
                item1 = types.KeyboardButton('✉ Мои планы')
                item2 = types.KeyboardButton('📚 Информация')
                markup.add(item1, item2)

                bot.send_message(chat_id, 'У вас нет планов', reply_markup=markup)

            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                bot.register_next_step_handler(message, delete)
                item1 = types.KeyboardButton('✉ Мои планы')
                item2 = types.KeyboardButton('📚 Информация')

                markup.add(item1, item2)

                bot.send_message(chat_id, 'Какой план вы хотите отменить? (Напишите)', reply_markup=markup)

        elif message.text == '🤔 Когда напоминание?':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')

            markup.add(item1, item2)
            if chat_id not in plans or not plans[chat_id]:
                bot.send_message(message.chat.id, 'Сначала добавьте план', reply_markup=markup)

            else:
                bot.send_message(message.chat.id, 'Время напоминания какого плана вы хотите узнать? (Напишите)',
                                 reply_markup=markup)
                bot.register_next_step_handler(message, nap)


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
            bot.send_message(chat_id, "План добавлен")
        else:
            bot.send_message(chat_id, 'Некорректный ввод. Попробуйте еще раз')
            bot.register_next_step_handler(message, add_to_list)
    else:
        bot.send_message(chat_id, 'Некорректный ввод. Попробуйте еще раз')
        bot.register_next_step_handler(message, add_to_list)


def delete(message):
    chat_id = message.chat.id
    del_plan = message.text
    if del_plan in plans[chat_id]:
        n = plans[chat_id].index(del_plan)

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
        bot.send_message(message.chat.id,
                         f'Напоминание о плане {plans[chat_id][x]} придет {plans[chat_id][x + 1][:10]} числа'
                         f' в {plans[chat_id][x + 1][11:]}')
    else:
        bot.send_message(message.chat.id, 'Такого плана нет')


def check_plans():
    current_time = dt.datetime.now()
    for z in list(plans.keys()):
        for plan in plans[z][::2]:
            n = plans[z].index(plan)
            if len(plans[z]) - 1 > n:
                date_time_obj = dt.datetime.strptime(plans[z][n + 1], '%d.%m.%Y %H:%M')
                if current_time > date_time_obj:
                    bot.send_message(z, f"Время для плана {plan} наступило.\nСкорее выполните его!")
                    plans[z].remove(plan)
                    plans[z].remove(plans[z][n])

    threading.Timer(15, check_plans).start()


check_plans()

bot.infinity_polling()
