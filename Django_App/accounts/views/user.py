"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-30 00:07:20 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import io
from django.http import HttpResponse
from django.views import View
from django.db.models import F, Q
from django.contrib.auth import (
    get_user_model, authenticate, login as django_login, logout as django_logout)
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly,
)
from accounts.serializers import UserSerializer, UserCustomInfoSerializer

from utils.logger import LOG
from utils.func import generate_sha256_identifier
from utils.captcha import ImageCaptchaGenerator
from utils.utils import Paginator


User = get_user_model()


class LoginView(APIView):
    """用户登录"""
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, template_name="login.html")

    def post(self, request):
        # 获取表单数据
        role = request.data.get('role')
        mobile = request.data.get('mobile')
        pwd = request.data.get('pwd')
        LOG.debug(f"role:{role}, mobile:{mobile}, pwd:{pwd}")
        # 验证用户
        user = authenticate(request, mobile=mobile, password=pwd, role=role)
        if not user:
            # 用户不存在或信息错误
            return Response({"code": 40099, "success": False, "error": ["用户信息校验失败", "用户名或密码错误"]}, status=400)
        else:
            # 绑定登录状态
            django_login(request, user)  # 用Django内置login函数绑定request.user与当前用户
            # 成功响应
            response = Response({
                "code": 20099,
                "success": True,
                "message": "登录成功",
                "data": {"1": "11"}
            })
            # 设置Cookies
            response.set_cookie(
                key="user_auth",
                value=user.id,
                max_age=60 * 60 * 24 * 7,  # 有效期：7天
                httponly=True,  # 关键：禁止JS读取，防XSS攻击
                secure=request.is_secure(),  # 生产环境启用（HTTPS下才生效）
                samesite="Lax",  # 限制跨站请求，防CSRF攻击
                path="/",
            )
            return response


class LogoutApiView(APIView):
    """用户退出登录"""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_identity):
        django_logout(request)
        # 清理自定义 Cookie
        response = Response({"code": 20003, "success": True, "message": "成功退出登录状态"})
        if 'user_auth' in request.COOKIES:  # 只清理存在的自定义 Cookie
            response.delete_cookie('user_auth')

        # 验证登录状态结果
        if not request.user.is_authenticated:
            return response
        else:
            return Response({"code": 50003, "success": False, "error": "退出登录失败，会话清理异常"}, status=500)


class RegisterApiView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()  # strip() 去除前后空格
        password = request.POST.get("password", "").strip()
        mobile = request.POST.get("mobile", "").strip()

        # 数据格式验证
        serializer = UserCustomInfoSerializer(data={"name": username, "password": password, "mobile": mobile})
        if not serializer.is_valid(raise_exception=True):
            return Response({"code": 40002, "success": False, "error": serializer.errors}, status=400)

        # 检查用户名/手机号是否已存在
        # 用 Q() 实现“或”逻辑，避免两次数据库查询（优化性能）
        duplicate_user = User.objects.filter(Q(name=username) | Q(mobile=mobile)).only("name", "mobile").first()
        if duplicate_user:
            # 判断具体重复字段
            if duplicate_user.name == username:
                return Response({"code": 40004, "success": False, "error": "用户名已存在"}, status=400)
            if duplicate_user.mobile == mobile:
                return Response({"code": 40004, "success": False, "error": "手机号已被注册"}, status=400)

        # 生成用户标识
        user_identity = generate_sha256_identifier()

        # 用户信息写入数据库
        try:
            User.objects.create(
                user_identity=user_identity,
                mobile=mobile,
                password=password,
                name=username,
                role=2, # 默认客户
            )
        except Exception as e:
            return Response({"code": 50001, "success": False, "error": str(e)}, status=500)

        # 注册成功，重定向到登录页
        return redirect("/login/")


class CaptchaImage(View):
    """图片验证码"""
    def get(self, request):
        generator = ImageCaptchaGenerator(
            120, 40, font_size=30,
            char_length=4,
            font_file="accounts/static/fonts/JetBrainsMonoNerdFontMono-MediumItalic.ttf",
            angle_range=(-60, 60),
            interference_pixel_rate=0.20,
            interference_points=20,
            interference_lines=3,
            interference_circles=2,
        )
        code, image = generator.generate()
        stream = io.BytesIO()
        image.save(stream, format='JPEG')
        image = f"data:image/jpeg;base64,{generator.base64_image}"
        request.session['captcha_code'] = code
        return HttpResponse(stream.getvalue())



class UserListView(APIView):
    """用户列表"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # 查询用户信息并序列化
        active_users = User.objects.filter(is_deleted=0)
        active_users_list = UserSerializer(active_users, many=True).data
        deleted_users = User.objects.filter(is_deleted=1)
        deleted_users_list = UserSerializer(deleted_users, many=True).data
        return Response({
            "code": 20001,
            "success": True,
            "message": "",
            "data": {
                "active_users": active_users_list,
                "deleted_users": deleted_users_list
            }
        },)


@permission_classes([IsAdminUser])
class UserDeleteApiView(APIView):
    """用户删除"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, user_identity):
        # 校验参数
        if not user_identity or not isinstance(user_identity, str):
            return Response({"code": 40002, "success": False, "error": "用户标识格式错误"}, status=400)

        # 查询单个用户
        user = User.objects.filter(user_identity=user_identity).first()
        if not user:
            return Response({"code": 40499, "success": False, "error": "用户不存在"}, status=404)
        if user.is_deleted == 1:
            return Response({"code": 40901, "success": False, "error": "用户已删除，无需重复操作"}, status=409)
        # 执行逻辑删除操作
        try:
            user.is_deleted = 1
            user.is_active = False
            user.save()
            return Response({"code": 20003, "success": True, "message": "用户删除成功"})
        except Exception as e:
            return Response({"code": 50001, "success": False, "error": str(e)}, status=500)


@permission_classes([IsAuthenticated, IsAdminUser])
class UserRestoreApiView(APIView):
    """用户恢复"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_identity):
        # 校验参数
        if not user_identity or not isinstance(user_identity, str):
            return Response({"code": 40002, "success": False, "error": "用户标识格式错误"}, status=400)

        # 查询单个用户
        user = User.objects.filter(user_identity=user_identity).first()
        if not user:
            return Response({"code": 40499, "success": False, "error": "用户不存在"}, status=404)
        if user.is_deleted == 0:
            return Response({"code": 40901, "success": False, "error": "用户已恢复，无需重复操作"}, status=409)
        # 执行恢复操作
        try:
            user.is_deleted = 0
            user.is_active = True
            user.save()
            return Response({"code": 20002, "success": True, "message": "用户恢复成功"})
        except Exception as e:
            return Response({"code": 50001, "success": False, "error": str(e)}, status=500)


class UserHomeView(View):
    """用户个人主页"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_identity = request.user.user_identity

        user = get_object_or_404(
            User,
            user_identity=user_identity,
            is_deleted=0
        )
        return render(request, "user_homepage.html", {"user": user})


class UserCustomInfoUpdateApiView(APIView):
    """用户自定义信息更新"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # 校验表单
        new_custom_info = request.data.get('new_custom_info', {})
        if not new_custom_info:
            Response({"code": 40001, "success": False, "error": "请传递要更新的内容"}, status=400)
        serializer = UserCustomInfoSerializer(data=new_custom_info)
        if not serializer.is_valid():
            Response({"code": 40002, "success": False, "error": str(serializer.errors)}, status=400)

        # 获取登录用户标识
        user_identity = request.user.user_identity

        # 查询用户信息
        user = User.objects.filter(user_identity=user_identity).first()
        if not user:
            return Response({"code": 40499, "success": False, "error": "用户不存在"}, status=404)

        # 校验权限
        if not user.user_identity == user_identity:
            return Response({"code": 40302, "success": False, "error": "没有权限执行该操作"}, status=403)

        # 更新用户信息
        for field, value in serializer.validated_data.items():
            # 确保字段存在于模型中
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()

        return Response({"code": 20002, "success": True, "message": "用户信息更新成功"})
