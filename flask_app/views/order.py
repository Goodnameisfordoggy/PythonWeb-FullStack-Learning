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
from utils import db, cache, func
from utils.logger import LOG

ORDER_STATUS = {
    1: '待处理',
    2: '处理中',
    3: '成功',
    4: '失败',
}

# 创建蓝图对象
order = Blueprint('order', __name__)

@order.route('/order/list')
def order_list():
    user_info = session.get('user_info')
    role = user_info['role']
    data_list = []
    if role == 1: # 管理员
        data_list = db.fetch_all(
            "select * "
            "from `order` "
            "left join userinfo on `order`.user_identity = userinfo.user_identity ",
            []
        )
    elif role == 2: # 客户
        data_list = db.fetch_all(
            "select * "
            "from `order` "
            "left join userinfo on `order`.user_identity = userinfo.user_identity "
            "where user_identity=%s ",
            [user_info['user_identity'], ]
        )
    return render_template('order_list.html', order_list=data_list)

@order.route('/order/create', methods=['GET', 'POST'])
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
        # 写入 mysql
        db.insert_one(
            "insert into `order` (`order_identity`, `url`, `count`, `user_identity`, `status`) values (%s, %s, %s, %s, 1) ",
            [order_id, url, count, user_info['user_identity']]
        )
        # 写入 redis 队列
        cache.push_queue(order_id, "task_queue")
        LOG.info(f"用户:{user_info['user_identity']}成功创建了订单:{order_id}")
        # 准备弹窗内容
        session['show_modal'] = True
        session['modal_msg'] = f"订单 {order_id} 创建成功！"
    return redirect("/order/list")


@order.route('/order/delete/<order_id>', methods=['GET', ])
def order_delete(order_id):
    user_info = session.get('user_info')
    db.update_one(
        "update `order` set is_deleted=1 where order_identity=%s", [order_id, ])
    LOG.info(f"用户:{user_info['user_identity']}删除了订单:{order_id}")
    return redirect("/order/list")


@order.route('/api/clear-modal-session', methods=['POST'])
def clear_modal_session():
    """清除 Session 中的弹窗信号"""
    session.pop('show_modal', None)  # pop 方法：删除键并返回值，不存在则返回 None
    session.pop('modal_msg', None)
    return jsonify({"status": "success", "message": "modalSession已清除"})

