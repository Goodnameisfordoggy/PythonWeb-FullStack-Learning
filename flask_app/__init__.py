"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-07 22:10:43 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import os

from flask import Flask, session, redirect, request


def auth():
    """拦截器"""
    if request.path.startswith("/static"):
        return None
    if request.path == "/login":
        return None
    user_info = session.get('user_info')
    if user_info:
        return None
    # 拦截
    return redirect('/login')

def create_app():
    app = Flask(__name__,)
    app.secret_key = os.urandom(24)

    from .views import account
    from .views import order
    # 注册蓝图
    app.register_blueprint(account.account)
    app.register_blueprint(order.order)

    # 添加拦截器
    app.before_request(auth)

    return app