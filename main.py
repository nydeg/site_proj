from flask import Flask, render_template, redirect, url_for, request
from data import db_session
from data.users import User
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, current_user
from forms.login import LoginForm
from random import randint
from data.jobs import Jobs
import datetime as dt

LOGIN = False
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'random string'
reg = []
log = ''


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if LOGIN:
        return render_template("main.html", news="")
    else:
        return render_template("base.html", news="")


@app.post('/add')
def add():
    title = request.form.get('title')
    print(title)
    # мой способ
    db_sess = db_session.create_session()
    new_plan = Jobs(title=title, is_finished=False)
    # user = db_sess.query(User).filter(User.id == 1).first()
    # db_sess.add(new_plan)
    # user.jobs.append(new_plan)

    # 2 способ (работает)
    current_user.jobs.append(new_plan)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(url_for('index'))


# @app.get('/update/<int:todo_id>')
# def update(todo_id):
#     db_sess = db_session.create_session()
#     todo = Jobs.query.filter_by(id=todo_id).first()
#     todo.is_finished = not todo.is_complete
#     db_sess.commit()
#     return redirect(url_for('index'))


# @app.get('/delete/<int:todo_id>')
# def delete_r(todo_id):


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
            name=form.tg_name.data,
            email=form.email.data
        )
        reg.append(request.form.get('tg_name'))
        print(reg)
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
            global LOGIN, log
            LOGIN = True
            log = request.form.get('email')
            print(log)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/leave', methods=['GET', 'POST'])
def leave():
    global LOGIN
    LOGIN = False
    return render_template("base.html", news="")


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    global LOGIN
    LOGIN = False
    # тут надо прописать удаление аккаунта (из базы данных и в будущем из тг тоже)
    return render_template("base.html", news="")


def main():
    db_session.global_init("db/blogs.db")
    # user = User()
    # user.surname = "Scott"
    # user.name = "Ridley"
    # user.age = 21
    # user.position = "captain"
    # user.speciality = 'research engineer'
    # user.address = 'module_1'
    # user.email = 'scott_chief@mars.org'
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()

    # user = db_sess.query(User).filter(User.id == 1).first()
    # jobs = Jobs(team_leader=1, job='deployment of residential modules 1 and 2', work_size=15, collaborators='2, 3',
    #             start_date=dt.datetime.now(), is_finished=False)
    # db_sess.add(jobs)
    # user.jobs.append(jobs)
    # db_sess.commit()

    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Вторая новость", content="Уже вторая запись!",
    #             user=user, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()
    #
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Личная запись", content="Эта запись личная",
    #             is_private=True)
    # user.news.append(news)
    # db_sess.commit()

    app.run()


if __name__ == '__main__':
    main()
