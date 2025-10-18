"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-10-08 21:11:39 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""


def add_error(errors_dict, field, message):
    """
    给错误字典的指定字段添加错误信息。
    若字段不存在则自动初始化列表，存在则直接追加
    """
    if field not in errors_dict:
        # 首次添加：初始化列表
        errors_dict[field] = []
    # 追加错误信息
    errors_dict[field].append(message)