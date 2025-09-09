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
from flask import Blueprint, session, redirect, render_template
from utils import db

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
            "left join userinfo on `order`.user_id = userinfo.id ",
            []
        )
    elif role == 2: # 客户
        data_list = db.fetch_all(
            "select * "
            "from `order` "
            "left join userinfo on `order`.user_id = userinfo.id "
            "where user_id=%s ",
            [user_info['id'], ]
        )
    print(data_list)
    return render_template('order_list.html', order_list=data_list, user_name=user_info['name'])

@order.route('/order/create')
def order_create():
    return "创建订单"
