#coding:utf8
from flask import Blueprint

#创建蓝图对象
api = Blueprint('api_1_0',__name__,url_prefix='/api/1.0')

from . import verify,passport,profile,houses