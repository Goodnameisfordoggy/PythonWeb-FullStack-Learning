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


def authenticate():
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

    # 注册拦截器
    app.before_request(authenticate)

    # 注册模版全局变量：一次性定义，后续不会重新执行
    # app.add_template_global()

    # 注册上下文处理器：让变量在所有模板中可用
    @app.context_processor
    def inject_user_info():
        """每次渲染模板时，动态注册变量"""
        # 从 session 中获取用户信息
        user_info = session.get('user_info')
        if user_info:
            # 如果用户已登录，返回 user_name
            return {'user_name': user_info['name']}
        else:
            # 如果未登录，返回默认值（如“登录”）
            return {'user_name': '登录'}

    return app