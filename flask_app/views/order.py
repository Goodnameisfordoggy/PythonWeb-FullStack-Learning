"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-07 22:35:03 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from flask import Blueprint, session, redirect, render_template, request, jsonify
from utils import cache, func
from utils.logger import LOG
from flask_app.models import db, text, select, User, Order

ORDER_STATUS = {
    1: '待处理',
    2: '处理中',
    3: '成功',
    4: '失败',
}

# 创建蓝图对象
order_bp = Blueprint('order', __name__)

@order_bp.route('/order/list', methods=['GET', ])
def order_list():
    user_info = session.get('user_info')
    role = user_info['role']
    user_identity = user_info['user_identity']
    data_list = []
    if role == 1: # 管理员
        query = select(
            Order.id.label('order_id'),
            Order.order_identity,
            Order.create_time,
            Order.url,
            Order.count,
            Order.status,
            Order.is_deleted,
            User.id.label('user_id'),
            User.name,
        ).select_from(Order).join(
            User, Order.user_identity == User.user_identity, isouter=True
        )
        data_list = db.session.execute(query).mappings().all()
    elif role == 2: # 客户
        query = select(
            Order.id.label('order_id'),
            Order.order_identity,
            Order.create_time,
            Order.url,
            Order.count,
            Order.status,
            Order.is_deleted,
            User.id.label('user_id'),
            User.name,
        ).select_from(Order).join(
            User, Order.user_identity == User.user_identity, isouter=True
        ).where(
            Order.user_identity == user_identity,
        )
        data_list = db.session.execute(query).mappings().all()
    return render_template('order_list.html', data_list=data_list)


@order_bp.route('/order/create', methods=['GET', 'POST'])
def order_create():
    if request.method == 'GET':
        return render_template('order_create.html')
    elif request.method == 'POST':
        user_info = session.get('user_info')
        order_info = request.form
        url = order_info['url']
        count = order_info['count']
        # 生成唯一ID
        order_id = func.generate_sha256_identifier(f"{user_info['user_identity']}_{url}_{count}")
        # 写入数据库
        Order.create(
            order_identity=order_id,
            url=url,
            count=count,
            user_identity=user_info['user_identity'],
            status=1,
        )
        # 写入 redis 队列
        cache.push_queue(order_id, "task_queue")
        LOG.info(f"用户:{user_info['user_identity']}成功创建了订单:{order_id}")
        # 准备弹窗内容
        session['show_modal'] = True
        session['modal_msg'] = f"订单 {order_id} 创建成功！"
        return jsonify({"success": "true", "msg": f"订单创建成功"})
    else:
        return jsonify({"status": "true", "error": "不支持的请求类型"})

@order_bp.route('/order/delete/<order_identity>', methods=['DELETE', ])
def order_delete(order_identity):
    user_info = session.get('user_info')
    order = Order.get_by_order_identity(order_identity)
    if not order:
        return jsonify({"success": "false", "error": "订单不存在！"}), 404
    res, msg = Order.delete(order_identity)
    if not res:
        return jsonify({"success": "false", "error": msg}), 500
    LOG.info(f"用户:{user_info['name']}删除了订单:{order_identity}")
    return jsonify({"success": "true", "msg": f"订单删除成功"})

@order_bp.route('/api/clear-modal-session', methods=['POST'])
def clear_modal_session():
    """清除 Session 中的弹窗信号"""
    session.pop('show_modal', None)  # pop 方法：删除键并返回值，不存在则返回 None
    session.pop('modal_msg', None)
    return jsonify({"status": "success", "message": "modalSession已清除"})

