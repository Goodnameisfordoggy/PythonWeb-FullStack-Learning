"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-23 17:08:46 @PyCharm
Description: 序列化器

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from rest_framework import serializers
import accounts.models as accounts_models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 序列化的模型
        model = accounts_models.User
        # 全选字段
        # field = "__all__"
        # 指定字段，可动态调整
        fields = ['id', 'user_identity', 'create_time', 'mobile', 'password', 'name', 'role', 'is_deleted']
        # 排除字段，其余字段全选
        exclude = []
        # 指定只读字段
        read_only_fields = ['id', 'create_time']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = accounts_models.Order
        fields = ["id", "order_identity", "create_time", "url", "count", "user_identity", "status", "is_deleted"]
        read_only_fields = fields  # 响应字段均为只读


class OrderCreateRequestSerializer(serializers.Serializer):
    """订单创建请求数据校验序列化器"""
    url = serializers.URLField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)