# -*- coding:utf-8 -*-
#登录注册
import re

from flask import current_app
from flask import request, jsonify

from iHome import redis_store, db
from iHome.models import User
from iHome.until.response_code import RET
from . import api


@api.route('/users',methods=['POST'])
def register():
    """"注册
    1，获取注册参数：手机号，短信验证码，密码
    2，判断参数是否缺少
    3，获取服务器存储的短信验证码
    4，与客户端传入的短信验证码对比
    5，对比成功，创建User对象，给属性赋值
    6，将模型属性写入到数据库
    7，响应注册结果
    """

    #1，获取注册参数：手机号，短信验证码，密码
    #当确定前端发来的是json字符串
    json_dict = request.get_json()
    mobile = json_dict.get('mobile')
    sms_code_client = json_dict.get('sms_code_client')
    password = json_dict.get('password')

    #    2，判断参数是否缺少
    if not all([mobile,sms_code_client,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='缺少参数')
    if not re.match(r'[^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')

    #    3，获取服务器存储的短信验证码
    try:
        sms_code_server = redis_store.get('SMS:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询短信验证码失败')
    if not sms_code_server:
        return jsonify(errno=RET.NODATA,errmsg='短信验证码不存在')

    #    4，与客户端传入的短信验证码对比
    if sms_code_client != sms_code_server:
        return jsonify(errno=RET.PARAMERR,errmsg='短信验证码输入有误')

    # 5，对比成功，创建User对象，给属性赋值
    user = User()
    user.mobile = mobile
    user.name = mobile      #后面会有改用户名的逻辑
    # TODO 密码需要加密后加入到数据库
    user.password_hash = password

    # 6，将模型属性写入到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存用户注册数据失败')

    # 7，响应注册结果
    return jsonify(errno=RET.OK, errmsg='注册成功')





