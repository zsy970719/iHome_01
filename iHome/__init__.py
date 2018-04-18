#coding=utf-8
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from config import configs


# 创建连接到mysql数据库的对象
db = SQLAlchemy()

redis_store = None

def get_app(config_name):

    app = Flask(__name__)


    app.config.from_object(configs[config_name])

    #开启csrf保护
    CSRFProtect(app)

    #使用flask_session扩展session到Redis数据库
    Session(app)

    db.init_app(app)
    global redis_store
    # 创建连接到redis数据库的对象
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    #哪里需要蓝图就在哪里导入
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    from iHome.web_html import html_blue
    app.register_blueprint(html_blue)


    return app