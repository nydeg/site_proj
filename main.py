from flask import Flask, render_template, redirect, url_for, request
from data import db_session
from data.users import User
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, current_user
from forms.login import LoginForm
from data.jobs import Jobs
import datetime as dt
import sqlite3

LOGIN = False
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'random string'
log = ''
id_log = 0


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    todo_list = db_sess.query(Jobs).all()
    x = 1
    for i in todo_list:
        if i.connection == id_log:
            i.id = x
            x += 1

    if LOGIN:
        return render_template("main.html", todo_list=todo_list, id_log=id_log)
    else:
        return render_template("base.html")


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
            name=form.tg_name.data,
            email=form.email.data
        )
        # reg.append(request.form.get('tg_name'))
        # print(reg)
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
            global LOGIN, log, id_log
            LOGIN = True
            log = request.form.get('email')
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
    return render_template("base.html")


@app.route('/delete_acc', methods=['GET', 'POST'])
def delete_acc():
    global LOGIN
    LOGIN = False
    # тут надо прописать удаление аккаунта (из базы данных и в будущем из тг тоже)
    return render_template("base.html")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
