from django.views import View
from django.http import JsonResponse
from django.db.models import F, Q
from django.db import connection
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.sessions.backends.db import SessionStore
from django.views.decorators.http import require_POST
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts.models import User, Order, dict_fetchall
from accounts.permissions import IsAdminUser
from accounts.serializers import *
from utils.utils import *
from utils.logger import LOG
from utils.func import generate_sha256_identifier

class LoginView(View):
    """用户登录"""
    def get(self, request):
        return render(request, template_name="login.html")

    def post(self, request):
        # POST请求，处理登录逻辑
        # 获取表单数据
        role = request.POST.get('role')
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('pwd')

        # 校验用户信息
        user = User.objects.filter(role=role, mobile=mobile, password=pwd).first()
        if not user:
            # 用户不存在或信息错误
            return render(request, "login.html",{"error": "用户名或密码错误！"},)
        else:
            # 登录成功
            django_login(request, user)  # 用Django内置login函数绑定request.user与当前用户
            # 设置会话内容
            request.session['user_info'] = {
                "id": user.id,
                "user_identity": user.user_identity,
                "role": user.role,
                "name": user.name,
                "mobile": user.mobile,
            }
            # 重定向到订单列表页
            return redirect("/order/list/")


class LogoutApiView(APIView):
    """用户退出登录"""
    def post(self, request, user_identity):
        # 清除会话中的用户信息
        # request.session.pop("user_info", None)
        # 强制会话失效：完全清空会话
        request.session.flush()

        # 检查会话是否已清除
        if "user_info" not in request.session:
            LOG.debug("会话中的用户信息已清除")
            return Response({"success": True, "message": f"用户{user_identity}成功退出登录"})
        else:
            LOG.debug("会话中的用户信息未清除")
            return Response({"success": False, "error": "退出登录失败，请重试"}, status=500)


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()  # strip() 去除前后空格
        password = request.POST.get("password", "").strip()
        mobile = request.POST.get("mobile", "").strip()

        # 数据格式验证
        errors = {}
        if not username:
            errors["username"] = "用户名不能为空"
        elif len(username) < 3 or len(username) > 20:
            errors["username"] = "用户名长度必须在 3-20 个字符之间"
        if not password:
            errors["password"] = "密码不能为空"
        elif len(password) < 8:
            errors["password"] = "密码长度不能少于 8 位"
        if not mobile:
            errors["mobile"] = "手机号不能为空"
        elif not mobile.isdigit() or len(mobile) != 11:  # 补充：验证是否为纯数字
            errors["mobile"] = "请输入有效的 11 位手机号"
        if errors:
            return Response({"status": False, "error": errors}, status=400)

        # 检查用户名/手机号是否已存在
        # 用 Q() 实现“或”逻辑，避免两次数据库查询（优化性能）
        duplicate_user = User.objects.filter(Q(name=username) | Q(mobile=mobile)).only("name", "mobile").first()
        if duplicate_user:
            # 判断具体重复字段
            if duplicate_user.name == username:
                return Response({"status": False, "error": "用户名已存在"}, status=400)
            if duplicate_user.mobile == mobile:
                return Response({"status": False,"error": "手机号已被注册"}, status=400)
        # 用户信息写入数据库
        User.objects.create(
            user_identity=generate_sha256_identifier(),
            mobile=mobile,
            password=password,
            name=username,
            role=2,
        )
        # 注册成功，重定向到登录页
        return redirect("/login/")


@permission_classes([IsAdminUser])
class UserDeleteApiView(APIView):
    """用户删除"""
    def delete(self, request, user_identity):
        # 校验参数
        if not user_identity or not isinstance(user_identity, str):
            return Response({"success": False, "error": "用户标识格式错误"}, status=400)

        # 查询单个用户
        user = User.objects.filter(user_identity=user_identity).first()
        if not user:
            return Response({"success": False, "error": "用户不存在！"}, status=404)
        if user.is_deleted == 1:
            return Response({"success": False, "error": "用户已删除，无需重复操作！"}, status=400)
        # 执行逻辑删除操作
        try:
            user.is_deleted = 1
            user.is_active = False
            user.save()
            return Response({"success": True, "msg": "用户删除成功"})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)


@permission_classes([IsAdminUser])
class UserRestoreApiView(APIView):
    """用户恢复"""
    def post(self, request, user_identity):
        # 校验参数
        if not user_identity or not isinstance(user_identity, str):
            return Response({"success": False, "error": "用户标识格式错误"}, status=400)

        # 查询单个用户
        user = User.objects.filter(user_identity=user_identity).first()
        if not user:
            return Response({"success": False, "error": "用户不存在！"}, status=404)
        if user.is_deleted == 0:
            return Response({"success": False, "error": "用户已恢复，无需重复操作！"}, status=400)
        # 执行恢复操作
        try:
            user.is_deleted = 0
            user.is_active = True
            user.save()
            return Response({"success": True, "msg": "用户恢复成功"})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)

@permission_classes([IsAdminUser])
class UserListView(View):
    """用户列表"""

    def get(self, request):
        # 查询用户信息并序列化
        active_users = User.objects.filter(is_deleted=0)
        active_serializer = UserSerializer(active_users, many=True)
        deleted_users = User.objects.filter(is_deleted=1)
        deleted_serializer = UserSerializer(deleted_users, many=True)
        return render(
            request, template_name="user_list.html",
            context={"data": {"active_users": active_serializer.data, "deleted_users": deleted_serializer.data}}
        )


class UserHomeView(View):
    """用户个人主页"""
    def get(self, request):
        # 从session获取用户信息
        user_info = request.session.get('user_info')
        if not user_info:
            # 处理未登录情况，例如重定向到登录页
            return redirect('login')

        user = get_object_or_404(
            User,
            user_identity=user_info["user_identity"],
            is_deleted=0
        )
        return render(request, "user_homepage.html", {"user": user})


class OrderListView(View):
    """订单列表"""
    def get(self, request):
        # 获取当前登录用户信息
        user_info = request.session.get('user_info')
        if not user_info:
            # 如果session中没有用户信息，重定向到登录页
            return redirect('/login/')
        role = user_info['role']
        user_identity = user_info['user_identity']
        base_sql = ("SELECT "
                    "`order`.id AS order_id, "
                    "`order`.order_identity, "
                    "`order`.create_time, "
                    "`order`.url, "
                    "`order`.count, "
                    "`order`.status, "
                    "`order`.is_deleted, "
                    "userinfo.id AS user_id, "
                    "userinfo.name "
                    "FROM `order`"
                    "LEFT JOIN userinfo ON `order`.user_identity = userinfo.user_identity "
        )

        # 根据角色添加WHERE条件
        if role == 1:  # 管理员，查看所有订单
            sql = base_sql
            params = []
        else :  # 客户，只看自己的订单
            sql = f"{base_sql} WHERE `order`.user_identity = %s"
            params = [user_identity]

        # 执行SQL查询
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = dict_fetchall(cursor)
        # 将查询集转换为列表，便于模板处理
        data_list = list(result)
        return render(request, 'order_list.html', {'data_list': data_list})


class OrderCreateApiView(APIView):
    """
    订单创建
    """
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
                "code": 400,
                "success": False,
                "error": "参数校验失败",
                "detail": request_serializer.errors
            }, status=400)
        # 提取数据
        url = request_serializer.validated_data["url"]
        count = request_serializer.validated_data["count"]

        # 获取登录用户标识
        user_identity = user_identity = get_current_user_identity(request)

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
            return Response({"code": 500, "success": False, "error": str(e)}, status=500)

        # 写入 Redis 队列

        # 成功响应
        response_serializer = OrderSerializer(order)
        LOG.info(f"用户:{user_identity}成功创建了订单:{order_id}")
        return Response({
            "code": 201,
            "success": True,
            "msg": "订单创建成功",
            "data": response_serializer.data
        }, status=201)


class OrderDeleteApiView(APIView):
    """订单删除"""
    def delete(self, request, order_identity):
        # 校验参数
        if not order_identity or not isinstance(order_identity, str):
            return Response({"code": 400, "success": False, "error": "订单标识无效"}, status=400)

        # 获取登录用户标识
        user_identity = get_current_user_identity(request)

        # 查询订单
        order = Order.objects.filter(order_identity=order_identity).first()
        if not order:
            return Response({"code": 404, "success": False, "error": "订单不存在"}, status=404)

        # 校验订单归属
        if order.user_identity != user_identity:
            return Response({"code": 403, "success": False, "error": "没有权限执行该操作"}, status=403)

        # 校验订单状态
        if order.is_deleted == 1:
            return Response({"code": 403, "success": False, "error": "订单已删除，请勿重复操作"}, status=400)

        # 逻辑删除
        try:
            order.is_deleted = 1
            order.save()
        except Exception as e:
            LOG.error(f"删除订单失败: {str(e)}")
            return Response({"code": 500, "success": False, "error": "订单删除失败"}, status=500)

        # 成功响应
        LOG.info(f"用户[{user_identity}]成功删除订单[{order_identity}]")
        return Response({"code": 200, "success": True, "error": "订单删除成功"}, status=200)


