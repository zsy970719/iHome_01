#coding=utf-8
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
# from config import Develoment,Production,UnitTest
from config import configs

#创建数据库对象
db = SQLAlchemy()
#创建工厂
def get_app(config_name):

    app = Flask(__name__)


    app.config.from_object(configs[config_name])

    #开启csrf保护
    CSRFProtect(app)

    #使用flask_session扩展session到Redis数据库
    Session(app)

    #让数据库对象与app关联
    db.init_app(app)


    # 创建连接到redis数据库的对象
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    #在工厂里做好了东西要拿出去
    return app