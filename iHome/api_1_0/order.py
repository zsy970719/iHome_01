# -*- coding:utf-8 -*-
# 订单
from datetime import datetime

from flask import request, jsonify, current_app, g

from iHome import db
from iHome.models import House, Order
from iHome.until.response_code import RET
from . import api
from iHome.until.common import login_required


@api.route('/orders', methods=['GET'])
@login_required
def get_order_list():
    # 1
    user_id = g.user_id

    # 2
    try:
        orders = Order.query.filter(Order.user_id==user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')

    # 3
    order_dict_list = []
    for order in orders:
        order_dict_list.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg='ok', data=order_dict_list)


@api.route('/orders', methods=["POST"])
@login_required
def create_order():
    """创建，提交订单
    0，判断用户是否登录
    1，获取参数:house_id,start_date,end_date
    2，判断参数是否为空
    3，校验时间格式是否合法
    4，通过house_id,判断要提交的房屋是否存在
    5，判断当前的房屋是否被预定
    6，创建订单模型对象，并赋值
    7，将数据保存到数据库
    8，响应提交订单结果
    """
    # 1
    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_date_str = json_dict.get('start_date')
    end_date_str = json_dict.get('end_date')

    # 2
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date, Exception('入住时间有误')

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='入住时间有误')

    # 4
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')
    if not house_id:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 5
    try:
        conflict_orders = Order.query.filter(Order.house_id == house_id, Order.begin_date < end_date,
                                             Order.end_date > start_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')
    if conflict_orders:
        return jsonify(errno=RET.PARAMERR, errmsg='该房屋已经被预定了')

    # 6
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = (end_date - start_date).days  # days是datetime模块中的属性
    order.house_price = house.price
    order.amount = order.days * house.price

    # 7.将数据保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单数据失败')

    # 8.响应提交订单结果
    return jsonify(errno=RET.OK, errmsg='OK')
