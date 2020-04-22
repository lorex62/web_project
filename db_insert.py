from data import db_session
from data.users import User
from datetime import date

db_session.global_init("db/blogs.sqlite")
user = User()
user.name = "Пользователь 3"
user.about = "биография пользователя 3"
user.email = "email3@email.ru"
session = db_session.create_session()
session.add(user)
session.commit()