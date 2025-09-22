"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-13 23:53:30 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, select

db = SQLAlchemy()

from .user import User
from .order import Order


# 统一暴露公共接口（方便外部导入）
__all__ = [
    'db',
    'text',
    'select',
    'User',
    'Order',
]
