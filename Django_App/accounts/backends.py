"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-27 11:54:13 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    """自定义后端认证"""
    def authenticate(self, request, **kwargs):
        # 提取认证所需的参数
        mobile = kwargs.get('mobile')
        password = kwargs.get('password')

        if not mobile or not password:
            return None  # 缺少必要参数，直接返回失败

        try:
            # 根据业务逻辑查询用户（例如通过手机号）
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return None  # 用户不存在

        # 验证密码+用户是否激活
        # if user.check_password(password) and self.user_can_authenticate(user):
        #     return user
        # return None
        if user.password == password and self.user_can_authenticate(user):
            return user
        return None

    # 显示实现父类方法
    def get_user(self, user_id):
        """登录后获取 user"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None