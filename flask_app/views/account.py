"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-07 22:34:55 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from flask import Blueprint, render_template, request, redirect, session
from utils.db import fetch_one
from utils.logger import LOG

# 创建蓝图对象
account = Blueprint('account', __name__ )

@account.route('/login', methods=['GET', 'POST'])
def login():
    # GET请求，进入登录页面
    if request.method == 'GET':
        return render_template("login.html")

    # POST请求，获取表单信息
    elif request.method == 'POST':
        role = request.form['role']
        mobile = request.form['mobile']
        pwd = request.form['pwd']
        LOG.success(f"role:{role} mobile:{mobile} pwd:{pwd}")
        # 校验用户信息
        user_info = fetch_one(
            "select * from userinfo where role=%s and mobile=%s and password=%s",
            [role, mobile, pwd]
        )
        if not user_info:
            return render_template("login.html", error="用户名或密码错误！")
        else:
            session["user_info"] = {
                "id": user_info["id"],
                "role": user_info["role"],
                "name": user_info["name"],
                "mobile": user_info["mobile"],
            }
            return redirect("/order/list")

@account.route('/users')
def users():
    return "用户列表"