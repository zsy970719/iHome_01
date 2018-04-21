# -*- coding:utf-8 -*-
#个人中心
from flask import current_app, jsonify
from flask import session

from iHome.models import User
from iHome.until.response_code import RET
from . import api


@api.route('/users',methods=['GET'])
def get_user_info():
    """提供个人信息
    0.TODO 判断用户是否登录
    1.从session中获取当前登录用户的user_id
    2.查询当前登录用户的user信息
    3.构造个人信息的响应数据
    4.响应个人信息的结果
    """
    #1.从session中获取当前登录用户的user_id
    user_id = session['user_id']

    #2.查询当前登录用户的user信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='用户不存在')

    #3.构造个人信息的响应数据
    response_info_dict = user.to_dict()

    #4.响应个人信息的结果
    return jsonify(errno=RET.OK,errmsg='OK',data = response_info_dict)




