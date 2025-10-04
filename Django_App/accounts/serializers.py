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
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

import accounts.models as accounts_models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 序列化的模型
        model = get_user_model()
        # 全选字段
        # field = "__all__"
        # 指定字段，可动态调整
        fields = ['id', 'user_identity', 'create_time', 'mobile', 'name', 'role', 'is_deleted']
        # 排除字段，其余字段全选
        exclude = []
        # 指定只读字段
        read_only_fields = ['id', 'create_time']


class UserCustomInfoSerializer(serializers.Serializer):
    # 昵称
    nickname = serializers.CharField(
        max_length=32,
        required=False,
        allow_null=True,
        error_messages={
            "max_length": "昵称不能超过32个字符",
        }
    )
    # 头像
    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            "invalid": "请上传有效的图片文件（支持JPG、PNG等格式）",
            "max_size": "图片大小不能超过2MB"  # 可结合自定义校验限制大小
        }
    )
    # 头像URL（若头像存储在云服务，返回URL）
    # avatar = serializers.URLField(
    #     required=False,
    #     allow_null=True,
    #     allow_blank=False,
    #     error_messages={"invalid": "头像URL格式不正确"}
    # )
    # 个性签名
    signature = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "max_length": "个性签名不能超过100个字符",
        }
    )
    # 手机号
    mobile = serializers.CharField(
        max_length=11,
        min_length=11,
        required=False,
        error_messages={
            "max_length": "手机号必须为11位数字",
            "min_length": "手机号必须为11位数字",
            "blank": "手机号不能为空"
        }
    )
    # 邮箱
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        error_messages={
            "invalid": "邮箱格式不正确（如：example@domain.com）",
        }
    )
    # 密码
    password = serializers.CharField(
        max_length=128,
        required=False,
        write_only=True,  # 序列化返回时不包含密码（安全考虑）
        error_messages={
            "blank": "密码不能为空",
            "max_length": "密码长度不能超过128个字符"
        }
    )

    # 字段内容校验方法，命名格式 validate_<field>
    def validate_nickname(self, value):
        if value is not None:
            # 敏感词检测
            sensitive_words = []
            if any(word in value for word in sensitive_words):
                raise serializers.ValidationError({"nickname": ["昵称包含敏感词"]})
        return value

    def validate_mobile(self, value):
        if value is not None:
            if not re.match(r'^1[3-9]\d{9}$', value):
                raise serializers.ValidationError("手机号格式不正确（需为11位有效数字）")
        return value


    def validate(self, data):
        return data


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = accounts_models.Order
        fields = ["id", "order_identity", "create_time", "url", "count", "status", "user_identity", "is_deleted"]
        read_only_fields = fields  # 响应字段均为只读

    def get_status(self, obj):
        return obj.get_status_display()


class OrderRelatedUserSerializer(serializers.ModelSerializer):
    """订单关联的用户信息序列化器"""
    class Meta:
        model = get_user_model()
        fields = ["name", "user_identity"]


class OrderCreateRequestSerializer(serializers.Serializer):
    """订单创建请求数据校验序列化器"""
    url = serializers.URLField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)


