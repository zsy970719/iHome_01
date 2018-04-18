# -*- coding:utf-8 -*-
#图片验证和短信验证
from flask import abort, jsonify
from flask import make_response
from flask import request

from iHome import redis_store
from . import api
from iHome.until.captcha.captcha import captcha
from  iHome.until.response_code import RET



@api.route('/image_code',methods=['GET'])
def get_image_code():
    """提供图片验证码"""
    #1，获取uuid，并效验uuid
    uuid = request.args.get('uuid')
    if not uuid:
        abort(403)
    #2，上传图片验证码
    name, text, image = captcha.generate_captcha()
    #3，使用redis数据库缓存图片验证码，uuid作为key
    try:
        redis_store.set('ImageCode:%s'%uuid,text)
    except Exception as  e:
        print e
        return jsonify(errno=RET.DBERR,errmsg='保存验证码失败')

    #修改响应头信息，指定响应的内容是image/jpg
    response = make_response(image)
    response.headers['Content-Type']='image/jpg'


    #响应图片验证码
    return response