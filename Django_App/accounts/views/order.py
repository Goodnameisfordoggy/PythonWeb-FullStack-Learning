"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-30 00:07:29 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from django.db.models import F, Q
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import Order
from accounts.permissions import (
    IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly,
)
from accounts.serializers import (
    OrderSerializer, OrderRelatedUserSerializer, OrderCreateRequestSerializer,
)
from utils.logger import LOG
from utils.func import generate_sha256_identifier
from utils.utils import Paginator

User = get_user_model()


class OrderListApiView(APIView):
    """订单列表"""
    permission_classes = [IsAuthenticated]
    PAGE_SIZE: int = 10

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
                description=f'搜索关键词，支持字段：{", ".join(Order.ALLOWED_SEARCH_FIELDS)}（模糊匹配）',
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def get(self, request):
        page = request.GET.get('page', 1)
        search = request.GET.get('search', '').strip()
        # 获取当前登录用户信息
        role = request.user.role
        user_identity = request.user.user_identity
        # 基础查询条件
        order_base_condition = {'user_identity': user_identity, "is_deleted": 0}
        # 模糊匹配条件
        order_search_conditions = Q()  # 初始化空条件
        if search:
            # 对每个允许的字段进行 icontains 模糊匹配
            for field_name in Order.ALLOWED_SEARCH_FIELDS:
                if field_name:
                    order_search_conditions |= Q(**{f"{field_name}__icontains": search})
        # 查询用户
        user = User.objects.filter(user_identity=user_identity).first()
        if role == 1: # 管理员
            # 查询全部订单数据
            all_users_orders = Order.objects.filter(order_search_conditions)
            # 初始化分页工具
            paginator = Paginator(all_users_orders, page, self.PAGE_SIZE)
            # 序列化用户信息，提取用户唯一标识为 key
            all_users = User.objects.all()
            all_users_list = OrderRelatedUserSerializer(all_users, many=True).data
            all_users_map = {user["user_identity"]: user for user in all_users_list}
            # 序列化订单信息并插入关联用户信息
            orders_data = [
                {**order, "user_info": all_users_map.get(order["user_identity"], {}), }
                for order in OrderSerializer(paginator.paginated_data, many=True).data
            ]
        else:
            # 查询用户订单
            user_orders = Order.objects.filter(order_search_conditions, **order_base_condition)
            # 初始化分页工具
            paginator = Paginator(user_orders, page, self.PAGE_SIZE)
            # 序列化订单信息并插入关联用户信息
            orders_data = [
                {**order, "user_info": {**OrderRelatedUserSerializer(user).data}}
                for order in OrderSerializer(paginator.paginated_data, many=True).data
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
                "total_pages": paginator.total_pages,
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

        # 校验订单归属
        if not order or order.user_identity != user_identity:
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

