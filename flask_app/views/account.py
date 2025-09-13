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
from flask import Blueprint, render_template, request, redirect, session, jsonify
from utils.db import fetch_one
from utils.logger import LOG

# 创建蓝图对象
account = Blueprint('account', __name__ )

@account.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
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
                "user_identity": user_info["user_identity"],
                "role": user_info["role"],
                "name": user_info["name"],
                "mobile": user_info["mobile"],
            }
            return redirect("/order/list")
    else:
        return jsonify({"status": "true", "error": "不支持的请求类型"})


@account.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        # 1.获取表单信息
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        # 2.验证数据格式
        errors = {}
        if not username:
            errors['username'] = '用户名不能为空'
        elif len(username) < 3 or len(username) > 20:
            errors['username'] = '用户名长度必须在 3-20 个字符之间'
        if not password:
            errors['password'] = '密码不能为空'
        elif len(password) < 8:
            errors['password'] = '密码长度不能少于 6 位'
        if not mobile:
            errors['mobile'] = '手机号不能为空'
        elif len(mobile) != 11:  # 简单验证邮箱格式
            errors['mobile'] = '请输入有效的手机号'
        if errors:
            # 如果有验证错误，返回错误信息
            return jsonify({"status": "false", "errors": errors})
        # 3.检查数据是否存在
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "false", "error": "用户名已被注册"})

        if User.query.filter_by(email=email).first():
            return jsonify({"status": "false", "error": "邮箱已被注册"})
    else:
        return jsonify({"status": "true", "error": "不支持的请求类型"})

@account.route('/users')
def users():
    return "用户列表"