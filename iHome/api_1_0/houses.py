# -*- coding:utf-8 -*-
# 房屋模块
from flask import current_app, jsonify
from flask import g, session
from flask import request

from iHome import constants, redis_store
from iHome import db
from iHome.models import Area, House, Facility, HouseImage
from iHome.until.common import login_required
from iHome.until.image_storage import upload_image
from iHome.until.response_code import RET
from . import api


@api.route('/houses/search')
def get_house_search():
    """提供搜索资源
    0：无条件查询所有的房屋数据
    1：构造房屋数据
    2：响应数据
    """
    # 获取搜索使用的参数
    # 根据城区信息搜索房屋
    aid = request.args.get('aid')

    sk = request.args.get('sk', 'new')
    current_app.logger.debug(sk)

    p = request.args.get('p',1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数有误')


    try:
        house_query = House.query

        if aid:
            house_query = house_query.filter(House.area_id == aid)
        if sk == 'booking':  # 根据订单量由⾼到低
            house_query = house_query.order_by(House.order_count.desc())
        elif sk == 'price-inc':  # 价格低到⾼
            house_query = house_query.order_by(House.price.asc())
        elif sk == 'price-des':  # 价格⾼到低
            house_query = house_query.order_by(House.price.desc())
        else:  # 根据发布时间倒序
            house_query = house_query.order_by(House.create_time.desc())

        # houses = house_query.all()
        paginate = house_query.paginate(p,constants.HOUSE_LIST_PAGE_CAPACITY,False)
        houses = paginate.items
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')

    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    response_data = {
        'total_page':total_page,
        'houses':house_dict_list
    }

    return jsonify(errno=RET.OK, errmsg='ok', data=response_data)


@api.route('/houses/index')
def get_house_index():
    """主页房屋推荐
    1:直接查询最新的五个房屋：根据创建的时间倒叙，取前面五个
    """

    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋推荐数据失败')

    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='ok', data=house_dict_list)


@api.route('/areas', methods=["GET"])
def get_areas():
    """查询地区信息"""
    ###eval:会根据字符串的数据结构，自动生成对应结果的对象

    try:
        area_dict_list = redis_store.get('Areas')
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='ok', data=eval(area_dict_list))

    except Exception as e:
        current_app.logger.error(e)

    # 1，查询地区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询地区信息失败')

    # 2，将地区模型对象列表转成字典列表
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 缓存城区数据
    # 缓存是可有可无的，不能return。会影响主逻辑的运行
    try:
        redis_store.set('Areas', area_dict_list, constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 3,响应地区信息，只认识字典或者字典列表
    return jsonify(errno=RET.OK, errmsg='读取地区信息成功', data=area_dict_list)


@api.route('/houses', methods=["post"])
@login_required
def pub_house():
    """发布新的房源"""

    # 1，接受参数
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')
    facility = json_dict.get('facility')

    # 2，判断参数是否为空
    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days,
                facility]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        # 金额单位转成‘分’
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='金额格式错误')

    # 3，创建房屋模型对象
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facilities = Facility.query.filter(Facility.id.in_(facility)).all()
    house.facilities = facilities

    # 4，保存房源到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存房屋数据失败')

    # 5，响应发布的新的房源信息
    return jsonify(errno=RET.OK, errmsg='发布房源成功', data={'house_id': house.id})


@api.route('/houses/image', methods=["POST"])
@login_required
def upload_house_image():
    """上传房屋图片"""

    # 1,接受参数
    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传的参数')

    # 2，使用house_id，查询房屋信息，只有房屋存在，才能上传
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 3,调用上传图片的工具方法
    try:
        key = upload_image(image_data)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 4，创建HouseImage模型对象，并保存房屋图片key，保存到数据库
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    # 给房屋设置默认的图片
    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋图片失败')

    # 5，响应结果
    house_image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传房屋图片成功', data={'house_image_url': house_image_url})


@api.route('/houses/<house_id>', methods=['GET'])
def get_house_detail(house_id):
    """提供房屋详情数据

    """
    # 1.直接查询house_id对应的房屋信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2.构造房屋详情数据
    response_house_detail = house.to_full_dict()

    # 尝试获取登录用户信息，有可能未登录
    login_user_id = session.get('user_id', -1)

    # 3.响应房屋详情数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_house_detail, login_user_id=login_user_id)
