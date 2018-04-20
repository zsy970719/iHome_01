#coding=utf-8
from logging.handlers import RotatingFileHandler

import logging
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from config import configs
from iHome.until.common import RegexConverter


db = SQLAlchemy()

redis_store = None

def setUpLogging(level):
    # 设置⽇日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建⽇日志记录器器，指明⽇日志保存的路路径、每个⽇日志⽂文件的⼤大⼤大⼩小、保存的⽇日志⽂文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建⽇日志记录的格式                 ⽇日志等级    输⼊入⽇日志信息的⽂文件名 ⾏行行数    ⽇日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的⽇日志记录器器设置⽇日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的⽇日志⼯工具对象（flask app使⽤用的）添加⽇日志记录器器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):

    #根据开发环境设置日志等级
    setUpLogging(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)


    app.config.from_object(configs[config_name])

    #开启csrf保护
    # CSRFProtect(app)

    #使用flask_session扩展session到Redis数据库
    Session(app)

    db.init_app(app)
    global redis_store
    # 创建连接到redis数据库的对象
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    #需要现有正则，才能后面匹配
    app.url_map.converters['re'] = RegexConverter


    #哪里需要蓝图就在哪里导入
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    from iHome.web_html import html_blue
    app.register_blueprint(html_blue)


    return app