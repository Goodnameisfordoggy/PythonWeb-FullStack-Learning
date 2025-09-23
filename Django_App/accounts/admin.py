from django.contrib import admin
from accounts.models import User

# 简单注册，使用默认的 Admin 界面
# admin.site.register(User)


# 自定义 Admin 界面
@admin.register(User)  # 装饰器语法，等同于 admin.site.register(User, UserAdmin)
class UserAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('id', 'mobile', 'name', 'role', 'is_staff', 'is_active', 'create_time')

    # 可搜索的字段
    search_fields = ('mobile', 'name', 'user_identity')

    # 可筛选的字段
    list_filter = ('role', 'is_staff', 'is_active', 'is_deleted')

    # 列表页可直接编辑的字段
    list_editable = ('mobile', 'name', 'role', 'is_staff', 'is_active')

    # 详情页字段分组，避免表单过长
    fieldsets = (
        ('基础信息', {
            'fields': ('mobile', 'name', 'user_identity', 'create_time')
        }),
        ('权限设置', {
            'fields': ('is_staff', 'is_superuser', 'is_active')
        }),
        ('业务设置', {
            'fields': ('role', 'is_deleted')
        }),
    )

    # 设置只读字段
    readonly_fields = ('create_time',)