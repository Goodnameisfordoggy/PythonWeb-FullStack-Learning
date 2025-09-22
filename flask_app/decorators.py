"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-15 17:36:37 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
# decorators.py
from functools import wraps
from flask import abort, g
from flask_app.models import User


def admin_required(f):
    """检查用户是否为管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 正常状态：登录校验时已将用户信息存入 g.user
        if not hasattr(g, 'user') or not g.user or not isinstance(g.user, User):
            abort(401)  # 未登录
        # 检查用户角色是否为管理员
        if g.user.role != 1:
            abort(403)  # 权限不足
        return f(*args, **kwargs)
    return decorated_function