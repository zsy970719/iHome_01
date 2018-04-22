# -*- coding:utf-8 -*-
#定义公共的工具文件
from functools import wraps

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from iHome.until.response_code import RET


class RegexConverter(BaseConverter):
    #自定义路由转换器
    def __init__(self,url_map,*args):
        super(RegexConverter,self).__init__(url_map)
        #保存正则
        self.regex = args[0]


def login_required(view_func):
    """自定义装饰器判断用户是否登录

        使用装饰器时，会修改函数的__name__
    """

    @wraps(view_func)
    def wraaper(*args,**kwargs):
        """具体实现判断用户是否登录的逻辑"""
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')
        else:
            """执行被装饰的视图函数"""
            g.user_id = user_id
            return view_func(*args,**kwargs)

    return wraaper

