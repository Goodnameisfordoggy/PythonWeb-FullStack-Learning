"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-16 22:39:05 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from flask import jsonify, render_template
from flask.app import Flask


def register_errors(app: Flask):
    # 注册 405 错误处理器
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        print(e.description)
        allowed_methods = e.description.split(": ")[-1]
        return render_template('/errors/405.html', allowed_methods=allowed_methods), 405