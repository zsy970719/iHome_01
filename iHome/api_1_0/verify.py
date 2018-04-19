# -*- coding:utf-8 -*-
#图片验证和短信验证
import logging
from flask import abort, jsonify
from flask import current_app

from flask import make_response
from flask import request

from iHome import redis_store
from . import api
from iHome.until.captcha.captcha import captcha
from  iHome.until.response_code import RET
from iHome import constants


#定义变量记录上一次的uuid
last_uuid = ''


@api.route('/image_code',methods=['GET'])
def get_image_code():
    """提供图片验证码"""

    #1，获取uuid，并效验uuid
    uuid = request.args.get('uuid')
    if not uuid:
        abort(403)
    #2，上传图片验证码
    name, text, image = captcha.generate_captcha()
    # print text
    # logging.debug('AAA验证码为' + text)
    current_app.logger.debug('验证码为' + text)
    #3，使用redis数据库缓存图片验证码，uuid作为key
    try:
        if last_uuid:
            redis_store.delete('ImageCode:%s'%last_uuid)

        #过期时间为300秒
        redis_store.set('ImageCode:%s'%uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)
        # redis_store.delete('key:last_uuid')
    except Exception as  e:
        # print e
        # logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存验证码失败')

    #记录当前的uuid
    global last_uuid
    last_uuid = uuid

    #4，修改响应头信息，指定响应的内容是image/jpg
    response = make_response(image)
    response.headers['Content-Type']='image/jpg'
    #响应图片验证码
    return response