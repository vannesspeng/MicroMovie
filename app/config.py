import os

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/movie"  # 用于连接数据的数据库。
SQLALCHEMY_TRACK_MODIFICATIONS = True  # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
SECRET_KEY = 'vannesspeng'
UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
FC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")
REDIS_URL = 'redis://127.0.0.1:6379/0'
