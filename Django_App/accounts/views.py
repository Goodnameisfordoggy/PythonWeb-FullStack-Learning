from re import search

from django.views import View
from django.http import JsonResponse
from django.db.models import F, Q, Prefetch
from django.db import connection
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as django_login
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import Order
from accounts.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly,
)
from accounts.serializers import (
    UserSerializer, UserCustomInfoSerializer, OrderSerializer, OrderRelatedUserSerializer,
    OrderCreateRequestSerializer,
)
from utils.logger import LOG
from utils.func import generate_sha256_identifier

User = get_user_model()


class LoginView(APIView):
    """用户登录"""
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
            # 设置会话内容
            request.session['user_info'] = {
                "id": user.id,
                "user_identity": user.user_identity,
                "role": user.role,
                "name": user.name,
                "mobile": user.mobile,
            }
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
        # 清除 session
        # request.session.pop("user_info", None)
        request.session.flush()  # 强制会话失效：完全清空会话
        response = Response({"code": 20003, "success": True, "message": "成功退出登录状态"})

        # 清除 Cookies
        response.delete_cookie('sessionid')  # 清除 Django 默认的 sessionid Cookie
        response.delete_cookie('user_auth')  # 清除自定义的 Cookie

        if "user_info" not in request.session:
            LOG.debug("服务器端会话已清除")
            return response
        else:
            LOG.debug("服务器端会话清除失败")
            return Response({"code": 50003, "success": False, "error": "退出登录失败，会话清理异常"}, status=500)


class RegisterView(APIView):
    """用户注册"""
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


class UserHomeView(View):
    """用户个人主页"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 从session获取用户信息
        user_info = request.session.get('user_info')


        user = get_object_or_404(
            User,
            user_identity=user_info["user_identity"],
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


class OrderListView(APIView):
    """订单列表"""
    permission_classes = [IsAuthenticated]
    PAGE_SIZE: int = 10
    ALLOWED_SEARCH_FIELDS = ['url', '', 'product_name']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='页码（默认1）',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description=f'搜索关键词，支持字段：{", ".join(ALLOWED_SEARCH_FIELDS)}（模糊匹配）',
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def get(self, request):
        page = request.GET.get('page', 1)
        search = request.GET.get('search', '').strip()
        # 获取当前登录用户信息
        user_info = request.session.get('user_info')
        role = user_info['role']
        user_identity = user_info['user_identity']
        # 查询用户
        user = User.objects.filter(user_identity=user_identity).first()
        if role == 1:
            # 查询全部用户，订单数据
            all_users = User.objects.all()
            all_users_orders = Order.objects.all()
            # 序列化用户信息提取标识为 key
            all_users_list = OrderRelatedUserSerializer(all_users, many=True).data
            all_users_map = {user["user_identity"]: user for user in all_users_list}
            # 分页设置
            total_pages: int = len(all_users_orders) // self.PAGE_SIZE + 1
            orders_show = all_users_orders[(page - 1) * self.PAGE_SIZE:min(page * self.PAGE_SIZE, len(all_users_orders))]
            # 序列化订单信息并插入关联用户信息
            orders_data = [
                {**order, "user_info": all_users_map.get(order["user_identity"], {}), }
                for order in OrderSerializer(orders_show, many=True).data
            ]
        else:
            user_orders: list[Order] | None = user.orders
            # 分页设置
            total_pages: int = len(user_orders) // self.PAGE_SIZE + 1
            orders_show = user_orders[(page - 1) * self.PAGE_SIZE:min(page * self.PAGE_SIZE, len(user_orders))]
            # 序列化订单信息并插入关联用户信息
            orders_data = [
                {**order, "user_info": {**OrderRelatedUserSerializer(user).data}}
                for order in OrderSerializer(orders_show, many=True).data
            ]
            if not user:
                return Response({"code": 40499, "success": False, "error": "用户不存在"}, status=404)
        # 成功响应
        return Response({
            "code": 20001,
            "success": True,
            "message": f"{user.get_role_display()}{user.name}查询订单成功",
            "data": {
                "page": page,
                "total_pages": total_pages,
                "page_size": self.PAGE_SIZE,
                "orders": orders_data,
            },
        })


class OrderCreateApiView(APIView):
    """
    订单创建
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'order_create.html')

    # 登录校验
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 校验请求数据
        request_serializer = OrderCreateRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            # 校验失败：返回统一格式的错误信息
            return Response({
                "code": 40002,
                "success": False,
                "error": "参数校验失败",
                "detail": request_serializer.errors
            }, status=400)
        # 提取数据
        url = request_serializer.validated_data["url"]
        count = request_serializer.validated_data["count"]

        # 获取登录用户标识
        user_identity = request.user.user_identity

        # 生成唯一订单ID
        order_id = generate_sha256_identifier(f"{user_identity}_{url}_{count}")

        # 写入数据库
        try:
            order = Order.objects.create(
                order_identity=order_id,
                url=url,
                count=count,
                user_identity=user_identity,
                status=1
            )
        except Exception as e:
            # 捕获创建订单异常，返回错误信息
            LOG.error(f"用户:{user_identity}创建订单失败：{str(e)}")
            return Response({"code": 50001, "success": False, "error": str(e)}, status=500)

        # 写入 Redis 队列

        # 成功响应
        response_serializer = OrderSerializer(order)
        LOG.info(f"用户:{user_identity}成功创建了订单:{order_id}")
        return Response({
            "code": 20102,
            "success": True,
            "message": "订单创建成功",
            "data": response_serializer.data
        }, status=201)


class OrderDeleteApiView(APIView):
    """订单删除"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_identity):
        # 校验参数
        if not order_identity or not isinstance(order_identity, str):
            return Response({"code": 40002, "success": False, "error": "订单标识无效"}, status=400)

        # 获取登录用户标识
        user_identity = request.user.user_identity

        # 查询订单
        order = Order.objects.filter(order_identity=order_identity).first()
        if not order:
            return Response({"code": 40499, "success": False, "error": "订单不存在"}, status=404)

        # 校验订单归属
        if order.user_identity != user_identity:
            return Response({"code": 40302, "success": False, "error": "没有权限执行该操作"}, status=403)

        # 校验订单状态
        if order.is_deleted == 1:
            return Response({"code": 40901, "success": False, "error": "订单已删除，请勿重复操作"}, status=409)

        # 逻辑删除
        try:
            order.is_deleted = 1
            order.save()
        except Exception as e:
            LOG.error(f"删除订单失败: {str(e)}")
            return Response({"code": 50001, "success": False, "error": "订单删除失败"}, status=500)

        # 成功响应
        LOG.info(f"用户[{user_identity}]成功删除订单[{order_identity}]")
        return Response({"code": 20003, "success": True, "message": "订单删除成功"}, status=200)


