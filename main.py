from flask import Flask, render_template, redirect, url_for, request
from data import db_session
from data.users import User
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, current_user
from forms.login import LoginForm
from data.jobs import Jobs
import sqlite3
import multiprocessing as mp
import telebot
from telebot import types
import datetime as dt
import threading

bot = telebot.TeleBot('5830879893:AAGDZTLWWZwzzRkSFpWfUbTfYbL9TWHQehI')

plans = {}
LOGIN = False
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'random string'
id_log = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Да')
    item2 = types.KeyboardButton('Нет')

    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Здравствуй, {0.first_name}!\nЯ телеграм-бот, '
                                      'который поможет вам не забывать о планах\nВы '
                                      'уже зарегистрировались на сайте?'.format(message.from_user),
                     reply_markup=markup)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    if LOGIN:
        todo_list = db_sess.query(Jobs).all()
        return render_template("main.html", todo_list=todo_list, id_log=id_log, title='Главная страница')
    else:
        return render_template("base.html", title='Главная страница')


@app.post('/add')
def add():
    title = request.form.get('title')
    db_sess = db_session.create_session()
    new_plan = Jobs(title=title, is_finished=False)
    current_user.jobs.append(new_plan)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(url_for('index'))


@app.get('/update/<int:todo_id>')
def update(todo_id):
    db_sess = db_session.create_session()
    todo = db_sess.query(Jobs).filter(Jobs.id == todo_id).first()
    todo.is_finished = not todo.is_finished
    db_sess.commit()
    return redirect(url_for('index'))


@app.get('/delete/<int:todo_id>')
def delete(todo_id):
    db_sess = db_session.create_session()
    todo = db_sess.query(Jobs).filter(Jobs.id == todo_id).first()
    db_sess.delete(todo)
    db_sess.commit()

    con = sqlite3.connect('db/blogs.db')
    cur = con.cursor()
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

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            global LOGIN, id_log
            LOGIN = True
            log = request.form.get('email')
            with open('pass.txt', 'r+', encoding='utf8') as f:
                f.truncate(0)
                f.write(request.form.get('password'))
            con = sqlite3.connect('db/blogs.db')
            cur = con.cursor()
            id_log = cur.execute("""SELECT id FROM users WHERE email = ?""", (log, )).fetchone()[0]
            con.close()
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/leave', methods=['GET', 'POST'])
def leave():
    global LOGIN
    LOGIN = False
    return render_template("base.html", title='Главная страница')


@app.route('/delete_acc', methods=['GET', 'POST'])
def delete_acc():
    global LOGIN
    LOGIN = False
    # тут надо прописать удаление аккаунта (из базы данных и в будущем из тг тоже)
    return render_template("base.html", title='Главная страница')


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

        elif message.text == 'Да':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Да!')
            item2 = types.KeyboardButton('Пожалуй, не сейчас')
            markup.add(item1, item2)

            bot.send_message(chat_id, 'Хотите войти в аккаунт?', reply_markup=markup)

        elif message.text == 'Да!':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bot.register_next_step_handler(message, tg_login)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')
            markup.add(item1, item2)

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

        elif message.text == 'Пожалуй, не сейчас':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('✉ Мои планы')
            item2 = types.KeyboardButton('📚 Информация')

            markup.add(item1, item2)

            bot.send_message(chat_id, 'Чтобы понять как воспользоваться, перейдите в 📚 Информация',
                             reply_markup=markup)

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
                bot.register_next_step_handler(message, delete_plan)
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
    else:
        bot.send_message(chat_id, 'Нет пользователя с такой почтой. Попробуйте еще раз')
        bot.register_next_step_handler(message, tg_login)


def tg_password(message, email):
    chat_id = message.chat.id
    password = message.text
    with open('pass.txt', 'r', encoding='utf8') as f:
        curr_password = f.readline()
    if password == curr_password:
        bot.send_message(chat_id, "Вы вошли в аккаунт")
        if chat_id not in plans:
            con = sqlite3.connect('db/blogs.db')
            cur = con.cursor()
            result = cur.execute("""SELECT title FROM jobs
                            WHERE connection=(SELECT id from users WHERE email = ?)""", (email, )).fetchall()
            lst = []
            for i in result:
                lst.append(i[0])
                lst.append('')
            con.close()
            plans[chat_id] = lst
    else:
        bot.send_message(chat_id, 'Неправильный пароль. Попробуйте еще раз')
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
            check_plans()
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
        if plans[chat_id][x + 1] != '':
            bot.send_message(message.chat.id,
                             f'Напоминание о плане {plans[chat_id][x]} придет {plans[chat_id][x + 1][:10]} числа'
                             f' в {plans[chat_id][x + 1][11:]}')
        else:
            bot.send_message(message.chat.id, 'На этот план не установлено время напоминания')
    else:
        bot.send_message(message.chat.id, 'Такого плана нет')


def check_plans():
    current_time = dt.datetime.now()
    for z in list(plans.keys()):
        for plan in plans[z][::2]:
            n = plans[z].index(plan)
            if len(plans[z]) - 1 > n:
                if plans[z][n + 1] != '':
                    date_time_obj = dt.datetime.strptime(plans[z][n + 1], '%d.%m.%Y %H:%M')
                    if current_time > date_time_obj:
                        bot.send_message(z, f"Время для плана {plan} наступило.\nСкорее выполните его!")
                        plans[z].remove(plan)
                        plans[z].remove(plans[z][n])

    threading.Timer(15, check_plans).start()


def bot_func():
    bot.polling()


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    p = mp.Process(target=bot_func)
    p.start()
    app.run()
