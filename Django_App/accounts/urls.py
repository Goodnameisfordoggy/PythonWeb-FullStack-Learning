"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-23 01:06:22 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from django.urls import path

from accounts import views


api_urlpatterns = [
    path("user/logout/<str:user_identity>/", views.LogoutApiView.as_view(), name="api-user-logout"),
    path('user/delete/<str:user_identity>/', views.UserDeleteApiView.as_view(), name='api-user-delete'),
    path('user/restore/<str:user_identity>/', views.UserRestoreApiView.as_view(), name='api-user-restore'),
    path("order/create/", views.OrderCreateApiView.as_view(), name="api-order-create"),
    path("order/delete/<str:order_identity>/", views.OrderDeleteApiView.as_view(), name="api-order-delete"),
]

non_api_urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("order/list/", views.OrderListView.as_view(), name="order-list"),
    path("order/create/", views.OrderCreateApiView.as_view(), name="order-create"),
    path('user/list/', views.UserListView.as_view(), name='user-list'),
    path('user/homepage/', views.UserHomeView.as_view(), name='user-homepage'),
]


urlpatterns = [api_urlpatterns + non_api_urlpatterns]