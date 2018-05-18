# -*- coding:utf-8 -*-
# 订单
from datetime import datetime

from flask import request, jsonify, current_app, g

from iHome import db
from iHome.models import House, Order
from iHome.until.response_code import RET
from . import api
from iHome.until.common import login_required


@api.route('/orders/comment/<order_id>', methods=['POST'])
@login_required
def set_order_comment(order_id):
    """订单评价
    0,判断用户是否登录
    1，接受参数，order_id,comment并校验
    2，使用order_id查询待评价的订单数据
    3，修改订单状态为‘已完成’，并保存评价信息
    4，保存数据到数据库
    5，响应评价结果
    """
    # 1.接受参数：order_id，comment,并校验
    comment = request.json.get('comment')
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')

    # 2.使用order_id查询"待评价"的订单数据
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == 'WAIT_COMMENT',
                                   Order.user_id == g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 3.修改订单状态为"已完成"。并保存评价信息
    order.status = 'COMPLETE'
    order.comment = comment

    # 4.保存数据到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存评价信息失败')

    # 5.响应评价结果
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/orders/<order_id>', methods=['POST'])
@login_required
def set_order_status(order_id):
    """
    0，判断用户是否登录
    1，根据order_id查询订单信息，需要指定订单状态为‘待接单状态’
    2,修改订单状态为已接单
    3，保存到数据库
    4，响应结果
    """
    # 获取是接单还是拒单的操作
    action = request.args.get('action')
    if action not in ['accept', 'reject']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 1.根据order_id查询订单信息
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == 'WAIT_ACCEPT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询订单数据失败')
    if not order:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 2.判断当前登录是否是否是该订单中的房屋的房东
    login_user_id = g.user_id
    landlord_user_id = order.house.user_id
    if login_user_id != landlord_user_id:
        return jsonify(errno=RET.ROLEERR, errmsg='用户身份信息错误')

    # 3.修改订单状态为"已接单"
    if action == 'accept':
        order.status = 'WAIT_COMMENT'
    else:  # 拒单：修改订单状态为"已拒单",保存拒单理由
        order.status = 'REJECTED'
        reason = request.json.get('reason')
        if reason:
            order.comment = reason

    # 4.保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存订单状态到数据库失败')

    # 5.响应结果
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/orders', methods=['GET'])
@login_required
def get_order_list():
    # 接受用户信息
    role = request.args.get('role')
    if role not in ['custom', 'landlord']:
        return jsonify(errno=RET.PARAMERR, errmsg='用户身份错误')

    # 1
    user_id = g.user_id

    # 2
    try:
        if role == 'custom':  # 查询我的订单
            orders = Order.query.filter(Order.user_id == user_id)
        else:  # 查询客户订单
            # 获取该用户发布的房屋
            houses = House.query.filter(House.user_id == user_id).all()
            # 收集发布的房屋的house_id
            house_id = [house.id for house in houses]
            # 将在订单只能怪的房屋对应的订单查询出来
            orders = Order.query.filter(Order.house_id.in_(house_id)).all()
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
