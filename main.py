from django.shortcuts import redirect
from flask import Flask, make_response, request, session, render_template
from flask_login import LoginManager, login_user, current_user
from data import db_session
from data.users import User
import datetime
from loginform import LoginForm
from data.news import News





app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def index():
    # db_session.global_init("db/blogs.sqlite")
    # user = User()
    # user.name = "Пользователь 4"
    # user.about = "биография пользователя 4"
    # user.email = "email4@email.ru"
    # session = db_session.create_session()
    # session.add(user)
    # session.commit()
    # чтобы добавить пользователя, достаточно раскомментировать этот код и закомментировать строчку выше
    if current_user.is_authenticated:
        news = session.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = session.query(News).filter(News.is_private != True)
    return render_template('base.html')

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последнюю минуту")
        res.set_cookie("visits_count", '1',
                       max_age=60)
    return res

@app.route('/session_test/')
def session_test():
    if 'visits_count' in session:
        session['visits_count'] = session.get('visits_count') + 1
    else:
        session['visits_count'] = 1
    if session['visits_count'] >= 6:
        session.pop('visits_count', None)
        return 'вы посетили сайт более 6 раз, нам пох'
    return f"Вы посетили данный сайт {session['visits_count']} раз"

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')