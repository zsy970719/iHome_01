# -*- coding:utf-8 -*-
# 图片验证和短信验证
import logging
import random
import re
from flask import abort, jsonify
from flask import current_app
from flask import json
from flask import make_response
from flask import request
from iHome import redis_store
from . import api
from iHome.until.captcha.captcha import captcha
from  iHome.until.response_code import RET
from iHome import constants
from iHome.until.sms import CCP


@api.route('/sms_code', methods=['POST'])
def send_sms_code():
    """发送短信验证码
    1,和获取参数，手机号，验证码，uuid
    2，判断是否缺少参数，并对手机号格式进行效验
    3，获取服务器存储的验证码
    4，跟客户端发来的验证码做对比
    5，对比成功，生成短信验证码
    6，调用单列类发送短信
    7，如果发送短信成功，就保存短信验证码到redis数据库
    8，响应结果
    """

    # 1,和获取参数，手机号，验证码，uuid
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    imageCode_Client = json_dict.get('imageCode')
    uuid = json_dict.get('uuid')


    # 2，判断是否缺少参数，并对手机号格式进行效验
    if not all([mobile, imageCode_Client, uuid]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 3，获取服务器存储的验证码
    try:
        ImageCode_Server = redis_store.get('ImageCode:%s' % uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询验证码失败')
    if not ImageCode_Server:
        return jsonify(errno=RET.NODATA, errmsg='状态码不存在')

    # 4，跟客户端发来的验证码做对比
    if imageCode_Client.lower() != ImageCode_Server.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码输入错误')

    # 5，对比成功，生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    print '==='*20
    print u'短信验证码为：' + sms_code
    print '==='*20



    # # 6，调用单列类发送短信
    # result = CCP().send_sms_code(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], '1')
    # if result != 1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')


    # 7，如果发送短信成功，就保存短信验证码到redis数据库
    try:
        redis_store.set('SMS:%s' % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储短信验证码失败')

    # 8，响应结果
    return jsonify(errno=RET.OK, errmsg='发送短信验证码成功')


# 定义变量记录上一次的uuid
last_uuid = ''

@api.route('/image_code', methods=['GET'])
def get_image_code():
    """提供图片验证码"""

    # 1，获取uuid，并效验uuid
    uuid = request.args.get('uuid')
    if not uuid:
        abort(403)
    # 2，上传图片验证码
    name, text, image = captcha.generate_captcha()
    # print text
    # logging.debug('AAA验证码为' + text)
    current_app.logger.debug('验证码为' + text)
    # 3，使用redis数据库缓存图片验证码，uuid作为key
    try:
        if last_uuid:
            redis_store.delete('ImageCode:%s' % last_uuid)

        # 过期时间为300秒
        redis_store.set('ImageCode:%s' % uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        # redis_store.delete('key:last_uuid')
    except Exception as  e:
        # print e
        # logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')

    # 记录当前的uuid
    global last_uuid
    last_uuid = uuid

    # 4，修改响应头信息，指定响应的内容是image/jpg
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    # 响应图片验证码
    return response
