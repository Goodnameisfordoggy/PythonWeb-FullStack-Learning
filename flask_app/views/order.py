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
from flask import Blueprint, session, redirect

# 创建蓝图对象
order = Blueprint('order', __name__, url_prefix='/order')

@order.route('/list')
def order_list():
    return "订单列表"

@order.route('/create')
def order_create():
    return "创建订单"
