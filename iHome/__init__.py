#coding=utf-8
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from config import Develoment,Production,UnitTest



app = Flask(__name__)


app.config.from_object(Develoment)

#开启csrf保护
CSRFProtect(app)

#使用flask_session扩展session到Redis数据库
Session(app)

# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)

# 创建连接到redis数据库的对象
redis_store = redis.StrictRedis(host=Develoment.REDIS_HOST, port=Develoment.REDIS_PORT)
