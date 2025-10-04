"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-30 00:24:29 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from datetime import datetime
from django.db import models


class Order(models.Model):
    """订单模型"""
    objects = models.Manager()
    # 主键
    # id = models.AutoField(primary_key=True, verbose_name="订单ID")
    # 订单唯一标识
    order_identity = models.CharField(max_length=64, null=False, verbose_name="订单唯一标识")
    # 创建时间 auto_now=False=每次修改不更新
    create_time = models.DateTimeField(null=False, default=datetime.now, auto_now=False, verbose_name="创建时间")
    # 订单关联URL
    url = models.CharField(max_length=255, null=False, verbose_name="订单关联URL")
    # 数量/次数
    count = models.IntegerField(null=False, verbose_name="数量/次数")
    # 关联用户唯一标识
    user_identity = models.CharField(max_length=64, null=False, verbose_name="关联用户编号",
        help_text="关联用户的唯一标识user_identity"
    )
    # 订单状态
    STATUS_CHOICES = [(1, "待处理"), (2, "正在处理"), (3, "成功"), (4, "失败")]
    status = models.SmallIntegerField(null=False, choices=STATUS_CHOICES, verbose_name="订单状态")
    # 逻辑删除标记
    is_deleted = models.SmallIntegerField(null=False, default=0, verbose_name="逻辑删除标记", help_text="0=未删除，1=已删除")

    # 代码层面保护字段
    PROTECTED_FIELDS = {"id", "order_identity", "create_time", "user_identity"}
    ALLOWED_SEARCH_FIELDS = ['url', 'status']

    class Meta:
        db_table = "order"
        verbose_name = "订单"
        verbose_name_plural = verbose_name  # 中文单复数一致，直接复用
        # 添加索引优化查询
        indexes = [
            models.Index(fields=["order_identity"]),  # 订单唯一标识加索引，加速查询
            models.Index(fields=["user_identity"]),   # 关联用户编号加索引，加速用户订单查询
            models.Index(fields=["status"]),          # 订单状态加索引，加速按状态筛选
        ]

    def __str__(self):
        return f'<Order (标识: {self.order_identity}, 状态: {self.get_status_display()})>'