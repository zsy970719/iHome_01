# -*- coding:utf-8 -*-
# 房屋模块
from flask import current_app, jsonify
from flask import g
from flask import request

from iHome import db
from iHome.models import Area, House, Facility
from iHome.until.common import login_required
from iHome.until.response_code import RET
from . import api


@api.route('/areas', methods=["GET"])
def get_area():
    """查询地区信息"""
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

    # 3,响应地区信息
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
    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days,facility]):
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
    return jsonify(errno=RET.OK, errmsg='发布房源成功',data={'house_id':house.id})
