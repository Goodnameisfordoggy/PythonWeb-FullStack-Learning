from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    # 必须实现：创建用户、创建超级用户的方法
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError("必须提供手机号！")
        if 'role' not in extra_fields or extra_fields['role'] is None:
            raise ValueError("创建用户必须指定 role（1=管理员，2=客户）")
        user = self.model(mobile=mobile,** extra_fields)
        user.set_password(password)  # 密码哈希（来自 AbstractBaseUser）
        user.save()
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)  # 允许登录 admin
        extra_fields.setdefault('is_superuser', True)  # 超级用户权限
        extra_fields.setdefault('is_active', True)  # 账号启用
        extra_fields.setdefault('role', 1)
        extra_fields.setdefault('is_deleted', 0)
        # 校验关键字段，避免手动传入错误值
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        if extra_fields.get('role') != 1:
            raise ValueError('超级用户的 role 必须设为 1')

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """用户模型"""
    # 主键
    # id = models.AutoField(primary_key=True, verbose_name="用户ID")
    user_identity = models.CharField(max_length=64, null=False, verbose_name="用户唯一标识")
    # 创建时间
    create_time = models.DateTimeField(null=False, default=datetime.now, auto_now=False, verbose_name="创建时间")
    # 手机号
    mobile = models.CharField(max_length=11, null=False, unique=True, verbose_name="手机号")
    # 邮箱
    email = models.EmailField(null=True, unique=True, verbose_name="邮箱")
    # 密码
    password = models.CharField(max_length=128, null=False, verbose_name="登录密码")
    # 用户名
    name = models.CharField(max_length=32, null=False, verbose_name="用户名")
    # 昵称
    nickname = models.CharField(max_length=32, null=True, verbose_name="昵称")
    # 头像
    avatar = models.ImageField(upload_to="avatar", null=True, verbose_name="个人头像")
    # 个性签名
    signature = models.CharField(max_length=100, null=True, verbose_name="个性签名")
    # 角色
    ROLE_CHOICES = [(1, '管理员'), (2, '客户')]
    role = models.SmallIntegerField(choices=ROLE_CHOICES, null=False, verbose_name='用户角色', help_text='(1=管理员, 2=客户)')
    # 能否登录 admin
    is_staff = models.BooleanField(default=False, verbose_name='管理员权限')
    # 账号是否启用
    is_active = models.BooleanField(default=True, verbose_name="账号是否启用")
    # 逻辑删除标记：0=未删除，1=已删除
    is_deleted = models.SmallIntegerField(null=False, default=0, verbose_name="逻辑删除标记", help_text="0=未删除，1=已删除")

    objects = CustomUserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []  # 创建超级用户时必须提供的字段

    class Meta:
        # 数据库表名
        db_table = "userinfo"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=["user_identity"]),
        ]

    def __str__(self):
        return f'User (name: {self.name}, id: {self.id})'

    @property
    def orders(self):
        """获取用户的所有订单"""
        return Order.objects.filter(user_identity=self.user_identity)


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
    # PROTECTED_FIELDS = {"id", "order_identity", "create_time", "user_identity"}

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

    @property
    def userinfo(self):
        # 通过 user_identity 获取对应的用户信息
        return User.objects.filter(user_identity=self.user_identity).first()
