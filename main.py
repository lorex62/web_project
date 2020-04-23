from django.shortcuts import redirect
from flask import Flask, make_response, request, session, render_template, abort, jsonify, url_for
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data import db_session
from data.users import User
from data.new_from import NewsForm
import datetime
from loginform import LoginForm
from registerform import RegisterForm
from data.news import News
from data import news_api, user_api




db_session.global_init("db/users.sqlite")
app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def index():
    session = db_session.create_session()
    news = session.query(News)[::-1]
    return render_template('index.html', news=news, ln=len(news))

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

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

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой адрес почты уже занят")
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такое имя уже занято")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)

@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          (News.user == current_user) |
                                          (current_user.id == 1)).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          (News.user == current_user) |
                                          (current_user.id == 1)).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      (News.user == current_user) |
                                      (current_user.id == 1)).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')

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



@app.route('/user_login', methods=['POST'])
def user_login():
    login = request.form['login']
    if login is None or not login:
        return jsonify(data='Incorrect URL')

    try:
        c, conn = cursor_connection()
        c = conn.cursor()
        c.execute("SELECT accounts_info_uid "
                  "FROM auth_info WHERE login='{}' ".format(login))

        id = c.fetchall()
        if not id:
            return jsonify(data='Incorrect login')

        c.execute("SELECT * FROM boxes_id AS tb1 LEFT JOIN"
                  " accounts_info AS tb2 ON tb2.boxes_ids=tb1.uid "
                  # "LEFT JOIN electricity_info as tb3 ON tb3.boxes_id_uid=tb1.uid"
                  " WHERE tb2.uid={} ".format(id[0][0]))

        uid, mc_address, working_status, activation_status, _, \
        first_name, second_name, registration_date, phone, email, boxes_id = c.fetchall()[0]
        c.execute(" SELECT consumed_electricity "
                  "FROM electricity_info "
                  "WHERE boxes_id_uid={} ".format(boxes_id))
        consumed_electricity = [float(val[0]) for val in c.fetchall()]
        c.close()
        conn.close()

    except Exception as e:
        logger.error(msg='Cannot execute /user_login {}'.format(e))
        return str(e)

    user = User()
    user.id = login
    login_user(user)
    return redirect(url_for('welcome'))

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

'''def main():
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(news_api.blueprint)
    app.run()'''


if __name__ == '__main__':
    # main()
    app.run(port="8080", host='127.0.0.1')