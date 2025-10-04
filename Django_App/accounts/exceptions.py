"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-10-01 16:48:00 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler
from rest_framework.response import Response

class StructuredPermissionDenied(PermissionDenied):
    """自定义权限异常，携带额外信息（如code）"""
    def __init__(self, detail=None, biz_code=None):
        super().__init__(detail, biz_code)
        self.biz_code = biz_code


def custom_exception_handler(exc, context):
    # 先调用DRF默认的异常处理器，获取基础响应
    response = exception_handler(exc, context)

    # 处理自定义权限异常
    if isinstance(exc, StructuredPermissionDenied):
        # 构建结构化响应数据
        response_data = {
            "code": exc.biz_code,  # 业务状态码
            "success": False,
            "message": exc.detail  # 错误信息
        }
        # 返回结构化响应
        return Response(response_data, status=403)

    # 其他异常沿用默认处理
    return response