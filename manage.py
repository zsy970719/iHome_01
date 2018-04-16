#coding=utf-8
from flask import session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_wtf.csrf import CSRFProtect
from flask_session import Session


class Config(object):
    """封装配置的类"""
    DEBUG = True
    # mysql连接配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    # mysql禁⽌止追踪数据库增删改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis数据库配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SECRET_KEY = 'q6pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'

    # 指定存储session数据的数据库类型为redis
    SESSION_TYPE = 'redis'
    # 指定session数据存储到的位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名、混淆
    SESSION_USE_SIGNER = True
    # 设置session有效期:这里里里指的是session的扩展操作session时设置的有效期
    PERMANENT_SESSION_LIFETIME = 3600 * 24   # 一一天


app = Flask(__name__)


app.config.from_object(Config)

# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)

# 创建连接到redis数据库的对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

#将manager配置成Manager的对象
manager = Manager(app)

#在迁移是让app和db建立关联
Migrate(app,db)
#将迁移脚本添加到脚本管理器
manager.add_command('db',MigrateCommand)

#开启csrf保护
CSRFProtect(app)

#使用flask_session扩展session到Redis数据库
Session(app)





@app.route("/",methods=["GET","POST"])
def index():
    session['name'] = 'zsy'

    return "index"


if __name__ == '__main__':
    manager.run()