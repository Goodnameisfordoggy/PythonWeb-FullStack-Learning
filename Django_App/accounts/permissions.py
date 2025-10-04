"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-23 00:10:55 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from accounts.exceptions import StructuredPermissionDenied

class IsAdminUser(BasePermission):
    """
    管理员权限
    """
    message = "抱歉，您没有权限执行此操作，请联系管理员。"
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        raise StructuredPermissionDenied(detail=self.message, biz_code=40301)
