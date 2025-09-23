"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-23 22:27:06 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from rest_framework.response import Response

def get_current_user_identity(request):
    """
    验证并获取用户标识
    :param request: 请求对象
    :return: 验证通过返回user_identity，否则返回错误Response对象
    """
    user = request.user
    # 检查用户是否有user_identity属性且值有效
    if not hasattr(user, "user_identity") or not user.user_identity:
        return Response({
            "code": 400,
            "success": False,
            "error": "缺失用户标识"
        }, status=400)
    # 验证通过，返回用户标识
    return user.user_identity
